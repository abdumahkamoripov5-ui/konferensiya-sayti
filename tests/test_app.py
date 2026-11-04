"""Run with: python -m unittest discover -s tests -v (isolated SQLite only)."""
import csv
import io
import os
import re
import shutil
import tempfile
import unittest
import zipfile
import html
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('SECRET_KEY', 'test-only-secret-key-with-at-least-32-characters')
import config

# Redirect initialization before app import. Never open the project database.
ROOT = tempfile.TemporaryDirectory(prefix='konf-tests-')
config.Config.DATABASE = str(Path(ROOT.name) / 'empty.db')
config.Config.DATABASE_URL = ''
from app import app, csv_safe, email_togrimi
import models
from pypdf import PdfWriter
from uploads import validate_document


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('src', 'href') and value and value.startswith('/') and not value.startswith('//'):
                self.urls.add(value.split('#')[0])


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT.name)
        self.addCleanup(self.tmp.cleanup)
        db = str(Path(self.tmp.name) / 'case.db')
        shutil.copyfile(config.Config.DATABASE, db)
        app.config.update(TESTING=True, DATABASE=db, DATABASE_URL='',
                          MAQOLA_PAPKA=str(Path(self.tmp.name) / 'uploads'),
                          ADMIN_PAROL='test-admin-password', ADMIN_PASSWORD_HASH='',
                          SMTP_HOST='', PUBLIC_URL='', SESSION_COOKIE_SECURE=False,
                          SUBMISSIONS_OPEN=True, REGISTRATION_OPEN=True, MAX_CONTENT_LENGTH=20 * 1024 * 1024,
                          WTF_CSRF_ENABLED=True)
        app.config['MAX_UPLOAD_BYTES'] = config.Config.MAX_UPLOAD_BYTES
        self.client = app.test_client()
        self.deadline = patch.object(config, 'MUDDAT_ISO', '2099-11-15T23:59:59+05:00')
        self.deadline.start()
        self.addCleanup(self.deadline.stop)

    def token(self, path='/talablar', client=None):
        page = (client or self.client).get(path)
        match = re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True))
        self.assertIsNotNone(match)
        return match.group(1)

    def login(self):
        return self.client.post('/admin/kirish', data={
            'csrf_token': self.token('/admin/kirish'), 'login': 'admin', 'parol': 'test-admin-password'})

    def pdf(self):
        stream = io.BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.write(stream)
        return stream.getvalue()

    def upload(self, **overrides):
        data = dict(ism='Audit Author', email='test@example.com', sarlavha='Audit paper',
                    yonalish='1', csrf_token=self.token('/aloqa'), fayl=(io.BytesIO(self.pdf()), 'audit.pdf'))
        data.update(overrides)
        return self.client.post('/maqola-yuborish', data=data, content_type='multipart/form-data')

    def test_public_pages_and_all_local_assets(self):
        urls = set()
        for prefix in ('', '/en', '/tr'):
            for path in ('/', '/haqida', '/yonalishlar', '/kengash', '/talablar', '/aloqa', '/maqolalar'):
                response = self.client.get(prefix + path)
                self.assertEqual(response.status_code, 200, prefix + path)
                parser = LocalLinks()
                parser.feed(response.get_data(as_text=True))
                urls.update(parser.urls)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertLess(response.status_code, 400)
                response.close()

    def test_csrf_rejects_missing_and_cross_session_tokens(self):
        self.assertEqual(self.client.post('/aloqa', data={}).status_code, 400)
        other = app.test_client()
        self.assertEqual(other.post('/aloqa', data={'csrf_token': self.token('/aloqa')}).status_code, 400)
        self.login()
        self.assertEqual(self.client.post('/admin/ochirish/1').status_code, 400)
        self.assertEqual(self.client.get('/admin/chiqish').status_code, 405)

    def test_complete_submission_review_and_private_tracking(self):
        response = self.upload()
        self.assertEqual(response.status_code, 302)
        tracking = response.location
        self.assertIn('/maqola-holati/', tracking)
        private = app.test_client().get(tracking)
        self.assertEqual(private.status_code, 200)
        self.assertIn('no-store', private.headers['Cache-Control'])
        self.assertEqual(private.headers['Referrer-Policy'], 'no-referrer')
        self.assertEqual(self.client.get('/maqola/1/yuklab-olish').status_code, 302)
        self.assertEqual(self.login().status_code, 302)
        self.assertEqual(self.client.get('/admin').status_code, 200)
        for status in ('korib_chiqilmoqda', 'tuzatish_kerak', 'tasdiqlangan', 'rad_etilgan'):
            response = self.client.post('/admin/maqola/1/holat', data={
                'csrf_token': self.token('/admin'), 'holat': status, 'izoh': 'Review <script>alert(1)</script>'})
            self.assertEqual(response.status_code, 302)
            page = self.client.get(tracking).get_data(as_text=True)
            self.assertIn(config.MATN['uz']['holatlar'][status], html.unescape(page))
            self.assertNotIn('<script>alert(1)</script>', page)
            download = self.client.get('/maqola/1/yuklab-olish')
            self.assertEqual(download.status_code, 200 if status == 'tasdiqlangan' else 302)
            self.assertIn('no-store', download.headers['Cache-Control'])
            download.close()
        with app.app_context():
            self.assertEqual(len(models.maqolalar_tasdiqlangan()), 0)

    def test_invalid_document_track_and_preserved_form(self):
        response = self.upload(fayl=(io.BytesIO(b'fake PDF'), 'fake.pdf'), yonalish='invalid')
        self.assertEqual(response.status_code, 422)
        self.assertIn('value="Audit Author"', response.get_data(as_text=True))
        with app.app_context():
            self.assertEqual(models.maqolalar_royxati(), [])
        self.assertFalse(Path(app.config['MAQOLA_PAPKA']).exists())
        for ext, content in [('pdf', b''), ('doc', b'fake'), ('docx', b'fake')]:
            self.assertFalse(validate_document(content, ext))

    def test_docx_structure_and_bomb_limits(self):
        content_types = ('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                         '<Override PartName="/word/document.xml" '
                         'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                         '</Types>')
        def document(xml, other=None, types=content_types):
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('[Content_Types].xml', types)
                archive.writestr('word/document.xml', xml)
                if other:
                    archive.writestr(*other)
            return stream.getvalue()
        xml = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>'
        self.assertTrue(validate_document(document(xml), 'docx'))
        self.assertFalse(validate_document(document(xml, types='<Types/>'), 'docx'))
        self.assertFalse(validate_document(document(xml, types=content_types.replace(
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml',
            'application/vnd.ms-word.document.macroEnabled.main+xml')), 'docx'))
        self.assertFalse(validate_document(document(xml, ('word/VbaProject.bin', b'code')), 'docx'))
        self.assertFalse(validate_document(document('<fake/>'), 'docx'))
        self.assertFalse(validate_document(document(xml, ('word/vbaProject.bin', b'code')), 'docx'))
        self.assertFalse(validate_document(document(xml, ('bomb', b'0' * (51 * 1024 * 1024))), 'docx'))

    def test_email_control_characters_rejected_before_storage(self):
        for control in ('\x00', '\x01', '\x1f', '\x7f', '\r', '\n'):
            with self.subTest(control=repr(control)):
                self.assertFalse(email_togrimi('name' + control + '@example.com'))
        response = self.upload(email='name\x00@example.com')
        self.assertEqual(response.status_code, 422)
        with app.app_context():
            self.assertEqual(models.maqolalar_royxati(), [])

    def test_duplicate_upload_does_not_duplicate_or_leak_tracking(self):
        first = self.upload()
        second = self.upload(email='TEST@example.com')
        self.assertEqual(second.status_code, 409)
        self.assertNotIn(first.location, second.get_data(as_text=True))
        with app.app_context():
            self.assertEqual(len(models.maqolalar_royxati()), 1)
        self.assertEqual(len(list(Path(app.config['MAQOLA_PAPKA']).iterdir())), 1)

    def test_upload_above_four_mb_and_exact_file_limit(self):
        stream = io.BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.add_metadata({'/Subject': 'a' * (5 * 1024 * 1024)})
        writer.write(stream)
        content = stream.getvalue()
        app.config['MAX_UPLOAD_BYTES'] = len(content)
        self.assertEqual(self.upload(fayl=(io.BytesIO(content), 'large.pdf')).status_code, 302)
        self.login()
        self.assertIn('large.pdf', self.client.get('/admin').get_data(as_text=True))
        download = self.client.get('/admin/maqola/1/yuklab-olish')
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.data, content)
        download.close()
        app.config['MAX_UPLOAD_BYTES'] = len(content) - 1
        self.assertEqual(self.upload(fayl=(io.BytesIO(content), 'large.pdf')).status_code, 413)
        with app.app_context():
            self.assertEqual(len(models.maqolalar_royxati()), 1)

    def test_deadline_and_manual_close(self):
        with patch.object(config, 'MUDDAT_ISO', '2000-01-01T00:00:00+05:00'):
            self.assertEqual(self.upload(csrf_token=self.token('/aloqa')).status_code, 403)
        app.config['SUBMISSIONS_OPEN'] = False
        self.assertEqual(self.client.post('/maqola-yuborish', data={'csrf_token': self.token('/aloqa')}).status_code, 403)

    def test_login_rate_limit_and_no_default_password(self):
        app.config['ADMIN_PAROL'] = ''
        response = self.client.post('/admin/kirish', data={'csrf_token': self.token('/admin/kirish'), 'login': 'admin', 'parol': 'admin123'})
        self.assertEqual(response.status_code, 503)
        app.config['ADMIN_PAROL'] = 'test-admin-password'
        for i in range(4):
            self.assertEqual(self.client.post('/admin/kirish', data={'csrf_token': self.token('/admin/kirish'), 'login': 'admin', 'parol': 'wrong'}).status_code, 200)
        response = self.login()
        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response.headers)

    def test_contact_validation_rate_and_csv_safety(self):
        data = dict(csrf_token=self.token('/aloqa'), ism='=1+1', email='test@example.com', xabar='A long test message', mavzu='@SUM(1)')
        self.assertEqual(self.client.post('/aloqa', data={**data, 'xabar': 'x' * 5001}).status_code, 422)
        self.assertEqual(self.client.post('/aloqa', data=data).status_code, 302)
        self.login()
        data['csrf_token'] = self.token('/aloqa')
        rows = list(csv.reader(io.StringIO(self.client.get('/admin/eksport').get_data(as_text=True))))
        self.assertEqual(rows[1][1], "'=1+1")
        self.assertEqual(rows[1][3], "'@SUM(1)")
        for _ in range(3):
            self.client.post('/aloqa', data=data)
        self.assertEqual(self.client.post('/aloqa', data=data).status_code, 429)
        for value in (' =1', '\t=1', '\r@1', '-1', '+1'):
            self.assertTrue(csv_safe(value).startswith("'"))

    def test_admin_pagination_search_and_status_filter(self):
        with app.app_context():
            for i in range(25):
                models.xabar_qoshish(f'Name {i}', 'x@example.com', 'Subject', 'Message text')
                models.maqola_qoshish(f'Author {i}', 'x@example.com', f'Paper {i}', '', f'{i}.pdf', 'paper.pdf')
        self.login()
        for path in ('/admin', '/admin?xpage=2&mpage=2', '/admin?q=Author&maqola_holat=kutilmoqda'):
            self.assertEqual(self.client.get(path).status_code, 200)
        with app.app_context():
            page = models.paginated('papers', 2)
            self.assertEqual(len(page['rows']), 5)
            self.assertEqual(page['total'], 25)
            self.assertEqual(len(models.paginated('papers', search='Paper 24')['rows']), 1)
            self.assertEqual(models.paginated('papers', status='tasdiqlangan')['total'], 0)

    def test_oversize_calendar_and_404(self):
        token = self.token()
        app.config['MAX_CONTENT_LENGTH'] = 1024
        response = self.client.post('/maqola-yuborish', data={'csrf_token': token, 'fayl': (io.BytesIO(b'x' * 2048), 'large.pdf')})
        self.assertEqual(response.status_code, 413)
        self.assertIn('chegaradan oshdi', response.get_data(as_text=True))
        for path in ('/aloqa', '/en/royxatdan-otish', '/admin/kirish'):
            response = self.client.post(path, data={'csrf_token': token, 'xabar': 'x' * 2048})
            self.assertEqual(response.status_code, 413)
        for lang in ('', '/en', '/tr'):
            response = self.client.get(lang + '/taqvim.ics')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'DTEND;VALUE=DATE:20261217', response.data)
            self.assertTrue(all(len(line) <= 75 for line in response.data.split(b'\r\n')))
        self.assertEqual(self.client.get('/en/missing').status_code, 404)
        self.assertEqual(self.client.get('/maqola-holati/bogus').status_code, 404)

    def test_old_known_key_cannot_forge_session(self):
        from itsdangerous import URLSafeTimedSerializer
        from flask.sessions import SecureCookieSessionInterface
        interface = SecureCookieSessionInterface()
        serializer = URLSafeTimedSerializer('turkiy-yozma-meros-2026', salt=interface.salt,
            serializer=interface.serializer, signer_kwargs={'key_derivation': interface.key_derivation, 'digest_method': interface.digest_method})
        self.client.set_cookie(app.config['SESSION_COOKIE_NAME'], serializer.dumps({'admin': True}))
        self.assertEqual(self.client.get('/admin').status_code, 302)

    def test_optional_smtp_notification_is_mocked(self):
        app.config.update(SMTP_HOST='smtp.example.test', SMTP_FROM='conference@example.test', PUBLIC_URL='https://conference.example.test')
        with patch('notifications.smtplib.SMTP') as smtp:
            response = self.upload()
            self.assertEqual(response.status_code, 302)
            message = smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
            self.assertIn('https://conference.example.test/maqola-holati/', message.get_content())
            self.assertEqual(message['To'], 'test@example.com')

    def test_registration_consent_duplicates_and_admin_access(self):
        data = dict(csrf_token=self.token('/en/royxatdan-otish'), ism='Test Person',
                    email='person@example.com', tashkilot='Test University', format='online')
        self.assertEqual(self.client.post('/en/royxatdan-otish', data=data).status_code, 422)
        data['consent'] = 'yes'
        for _ in range(2):
            self.assertEqual(self.client.post('/en/royxatdan-otish', data=data).status_code, 302)
        self.assertEqual(self.client.get('/admin/qatnashchilar').status_code, 302)
        with app.app_context():
            self.assertEqual(models.paginated('participants')['total'], 1)
        self.login()
        page = self.client.get('/admin/qatnashchilar?q=University')
        self.assertEqual(page.status_code, 200)
        self.assertIn('Test Person', page.get_data(as_text=True))
        app.config['REGISTRATION_OPEN'] = False
        self.assertEqual(self.client.post('/royxatdan-otish', data={**data, 'csrf_token': self.token('/aloqa')}).status_code, 403)


if __name__ == '__main__':
    unittest.main()
