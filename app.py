# -*- coding: utf-8 -*-
"""«Turkiy yozma meros» xalqaro ilmiy yig'ini sayti — Flask ilovasi.

Sayt uch tilda ishlaydi: o'zbekcha manzil prefikssiz (`/haqida`),
inglizcha va turkcha prefiks bilan (`/en/haqida`, `/tr/haqida`).
"""

import csv
import io
import os
import re
import uuid
import secrets
import hashlib
import hmac
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime, timezone
from pathlib import Path
from functools import wraps

from flask import (Flask, flash, g, redirect, render_template, request,
                   Response, abort, send_file, send_from_directory, session, url_for)
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from uploads import validate_document
from notifications import notify_author

import config
import models

app = Flask(__name__)
app.config.from_object(config.Config)
if os.environ.get("VERCEL") or os.environ.get("APP_ENV") == "production":
    key = os.environ.get("SECRET_KEY", "")
    if len(key) < 32 or key == "turkiy-yozma-meros-2026":
        raise RuntimeError("Set a random SECRET_KEY of at least 32 characters in production.")
    app.config["SESSION_COOKIE_SECURE"] = True
if app.config["TRUSTED_PROXY_HOPS"]:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=app.config["TRUSTED_PROXY_HOPS"], x_proto=app.config["TRUSTED_PROXY_HOPS"])
csrf = CSRFProtect(app)


# Qo'shimcha tillar manzilda prefiks bo'lib turadi; o'zbekcha prefikssiz
QOSHIMCHA_TILLAR = "en,tr"


# --- Til qatlami -----------------------------------------------------------

@app.url_value_preprocessor
def tilni_ajratish(endpoint, values):
    """Manzildagi til prefiksini `g.til` ga oladi va argumentlardan olib tashlaydi."""
    g.til = (values or {}).pop("til", config.ASOSIY_TIL)


@app.url_defaults
def tilni_qoshish(endpoint, values):
    """`url_for` chaqiruvlariga joriy tilni avtomatik qo'shadi."""
    if "til" in values:
        return
    if app.url_map.is_endpoint_expecting(endpoint, "til"):
        values["til"] = g.get("til", config.ASOSIY_TIL)


def til_havolalari():
    """Har bir til uchun ayni shu sahifaning manzilini qaytaradi."""
    havolalar = {}
    args = {k: v for k, v in (request.view_args or {}).items() if k != "til"}
    for kod in config.TILLAR:
        try:
            if request.endpoint and app.url_map.is_endpoint_expecting(request.endpoint, "til"):
                havolalar[kod] = url_for(request.endpoint, til=kod, **args)
            else:
                havolalar[kod] = url_for("bosh_sahifa", til=kod)
        except Exception:
            havolalar[kod] = url_for("bosh_sahifa", til=kod)
    return havolalar


# --- Yordamchi funksiyalar -------------------------------------------------

def email_togrimi(email):
    return (len(email or "") <= 254
            and not any(ord(char) < 32 or ord(char) == 127 for char in (email or ""))
            and bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}", email or "")))


def admin_kerak(f):
    """Admin sahifalarini himoyalovchi dekorator."""
    @wraps(f)
    def orovchi(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_kirish"))
        return f(*args, **kwargs)
    return orovchi


@app.context_processor
def umumiy_kontekst():
    """Har bir shablonga joriy tildagi ma'lumotlarni uzatadi."""
    til = g.get("til", config.ASOSIY_TIL)
    return {
        "til": til,
        "t": config.MATN[til],
        "konf": config.KONFERENSIYA[til],
        "aloqa_malumot": config.ALOQA,
        "tillar": config.TILLAR,
        "til_havola": til_havolalari(),
        "sana_iso": config.SANA_ISO,
        "chorlov_fayl": config.CHORLOV_FAYL.get(til),
        "admin_kirgan": session.get("admin", False),
        "qabul_ochiq": qabul_ochiq(),
        "max_upload_bytes": app.config["MAX_UPLOAD_BYTES"],
        "public_origin": app.config["PUBLIC_URL"] or request.url_root.rstrip("/"),
        "rasm_bor": lambda name: bool(name) and (Path(app.static_folder) / "img" / "ekspertlar" / name).is_file(),
    }


# --- Ochiq sahifalar -------------------------------------------------------

@app.route("/", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/")
def bosh_sahifa():
    til = g.til
    return render_template(
        "index.html",
        faol="bosh",
        yonalishlar=config.royxat(config.YONALISHLAR, til),
        sanalar=config.royxat(config.MUHIM_SANALAR, til),
        xalqaro=config.royxat(config.XALQARO_KENGASH, til)[:4],
        ekspert_soni=len(config.XALQARO_KENGASH) + len(config.MAHALLIY_KENGASH),
        tashkilotchilar=config.TASHKILOTCHILAR[til],
        qahramon_surat=config.QAHRAMON_SURAT,
    )


@app.route("/haqida", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/haqida")
def haqida():
    til = g.til
    return render_template(
        "haqida.html",
        faol="haqida",
        maqsadlar=config.MAQSADLAR[til],
        tashkilotchilar=config.TASHKILOTCHILAR[til],
        sanalar=config.royxat(config.MUHIM_SANALAR, til),
    )


@app.route("/yonalishlar", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/yonalishlar")
def yonalishlar():
    return render_template(
        "yonalishlar.html",
        faol="yonalishlar",
        yonalishlar=config.royxat(config.YONALISHLAR, g.til),
    )


@app.route("/kengash", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/kengash")
def kengash():
    til = g.til
    return render_template(
        "kengash.html",
        faol="kengash",
        xalqaro=config.royxat(config.XALQARO_KENGASH, til),
        mahalliy=config.royxat(config.MAHALLIY_KENGASH, til),
        rasm_manbalari=config.RASM_MANBALARI,
    )


@app.route("/talablar", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/talablar")
def talablar():
    til = g.til
    return render_template(
        "talablar.html",
        faol="talablar",
        form={}, errors={},
        talablar=config.TALABLAR[til],
        eslatmalar=config.ESLATMALAR[til],
        yonalishlar=config.royxat(config.YONALISHLAR, til),
    )


@app.route("/aloqa", defaults={"til": config.ASOSIY_TIL}, methods=["GET", "POST"])
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/aloqa", methods=["GET", "POST"])
def aloqa():
    til = g.til
    if request.method == "POST":
        form = {
            "ism": (request.form.get("ism") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "mavzu": (request.form.get("mavzu") or "").strip(),
            "xabar": (request.form.get("xabar") or "").strip(),
        }
        enforce_rate("contact", 5, 600)
        if (not 2 <= len(form["ism"]) <= 150 or not email_togrimi(form["email"])
                or len(form["mavzu"]) > 200 or not 10 <= len(form["xabar"]) <= 5000):
            flash(config.MATN[til]["max_message"], "xato")
            return render_template("aloqa.html", faol="aloqa", form=form), 422

        models.xabar_qoshish(form["ism"], form["email"], form["mavzu"],
                             form["xabar"], til)
        flash(config.MATN[til]["muvaffaqiyat_forma"], "muvaffaqiyat")
        return redirect(url_for("aloqa"))

    return render_template("aloqa.html", faol="aloqa", form={})


def qabul_ochiq():
    return (app.config["SUBMISSIONS_OPEN"]
            and datetime.now(timezone.utc) <= datetime.fromisoformat(config.MUDDAT_ISO))


def enforce_rate(scope, limit, seconds):
    # Do not trust client-supplied forwarding headers. Configure the hosting proxy separately.
    allowed, retry = models.rate_limit(scope, request.remote_addr or "unknown", limit, seconds)
    if not allowed:
        response = render_template("xato.html", kod=429, xabar=config.MATN[g.til]["rate_error"])
        abort(Response(response, status=429, headers={"Retry-After": str(retry)}))


def submission_error(form, errors, status=422):
    til = g.til
    return render_template("talablar.html", faol="talablar", form=form, errors=errors,
                           talablar=config.TALABLAR[til], eslatmalar=config.ESLATMALAR[til],
                           yonalishlar=config.royxat(config.YONALISHLAR, til)), status


def tracking_url(paper):
    if not paper["tracking_token"] or not app.config["PUBLIC_URL"]:
        return ""
    return app.config["PUBLIC_URL"] + url_for("maqola_holati", til=paper["til"], token=paper["tracking_token"])


@app.route("/maqola-yuborish", defaults={"til": config.ASOSIY_TIL}, methods=["GET", "POST"])
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/maqola-yuborish", methods=["GET", "POST"])
def maqola_yuborish():
    til = g.til
    if request.method == "GET":
        return redirect(url_for("talablar", til=til) + "#yuborish")
    if not qabul_ochiq():
        return submission_error({}, {"general": config.MATN[til]["closed"]}, 403)
    enforce_rate("submission", 5, 600)
    form = {key: (request.form.get(key) or "").strip()
            for key in ("ism", "email", "sarlavha", "yonalish")}
    form["email"] = form["email"].lower()
    valid_tracks = {str(y["id"]) for y in config.YONALISHLAR}
    # Accept legacy track names as well as the new stable IDs.
    names = {y["nom"]: str(y["id"]) for y in config.royxat(config.YONALISHLAR, til)}
    form["yonalish"] = names.get(form["yonalish"], form["yonalish"])
    errors = {}
    if not 2 <= len(form["ism"]) <= 150:
        errors["ism"] = config.MATN[til]["field_error"]
    if not email_togrimi(form["email"]):
        errors["email"] = config.MATN[til]["field_error"]
    if not 3 <= len(form["sarlavha"]) <= 300:
        errors["sarlavha"] = config.MATN[til]["field_error"]
    if form["yonalish"] and form["yonalish"] not in valid_tracks:
        errors["yonalish"] = config.MATN[til]["field_error"]
    fayl = request.files.get("fayl")
    extension = fayl.filename.rsplit(".", 1)[-1].lower() if fayl and fayl.filename and "." in fayl.filename else ""
    data = fayl.read(app.config["MAX_UPLOAD_BYTES"] + 1) if fayl and extension in app.config["MAQOLA_KENGAYTMALAR"] else b""
    if len(data) > app.config["MAX_UPLOAD_BYTES"]:
        raise RequestEntityTooLarge()
    if not validate_document(data, extension):
        errors["fayl"] = config.MATN[til]["xato_fayl"]
    if errors:
        return submission_error(form, errors)
    token = secrets.token_urlsafe(32)
    filename = f"{uuid.uuid4().hex}.{extension}"
    original = secure_filename(fayl.filename)[:200] or f"maqola.{extension}"
    # Preserve a readable track label for existing admin/public views.
    track = next((y["nom"] for y in config.royxat(config.YONALISHLAR, til) if str(y["id"]) == form["yonalish"]), "")
    local_path = None
    try:
        if not app.config.get("DATABASE_URL"):
            os.makedirs(app.config["MAQOLA_PAPKA"], exist_ok=True)
            local_path = os.path.join(app.config["MAQOLA_PAPKA"], filename)
            with open(local_path, "xb") as handle:
                handle.write(data)
        paper_id = models.maqola_qoshish(form["ism"], form["email"], form["sarlavha"], track,
            filename, original, til, fayl_data=data, tracking_token=token,
            file_hash=hashlib.sha256(data).hexdigest())
        if paper_id is None:
            if local_path:
                os.remove(local_path)
            return submission_error(form, {"general": config.MATN[til]["duplicate"]}, 409)
    except Exception:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
        raise
    paper = models.maqola_topish(paper_id)
    flash(config.MATN[til]["muvaffaqiyat_maqola"], "muvaffaqiyat")
    if app.config["SMTP_HOST"]:
        sent = notify_author(paper, tracking_url(paper), config.MATN[til])
        flash(config.MATN[til]["mail_sent" if sent else "mail_failed"], "muvaffaqiyat" if sent else "xato")
    return redirect(url_for("maqola_holati", token=token))


@app.route("/maqola-holati/<token>", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/maqola-holati/<token>")
def maqola_holati(token):
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
        abort(404)
    paper = models.maqola_token_bilan(token)
    if paper is None:
        abort(404)
    return render_template("maqola_holati.html", paper=paper)


@app.route("/maqolalar", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/maqolalar")
def maqolalar_royxati():
    search = request.args.get("q", "").strip()[:100]
    listing = models.paginated("papers", request.args.get("page", 1, type=int), search, "tasdiqlangan")
    return render_template("maqolalar.html", faol="maqolalar", maqolalar=listing["rows"], listing=listing, search=search)


@app.route("/maqola/<int:maqola_id>/yuklab-olish")
def maqola_yuklab_olish(maqola_id):
    maqola = models.maqola_topish(maqola_id)
    if maqola is None or maqola["holat"] != "tasdiqlangan":
        return redirect(url_for("maqolalar_royxati"))
    return maqola_javobi(maqola)


def maqola_javobi(maqola):
    if app.config.get("DATABASE_URL"):
        data = models.maqola_fayli(maqola["id"])
        if data is None:
            abort(404)
        return send_file(io.BytesIO(data), as_attachment=True,
                         download_name=maqola["original_nomi"])
    return send_from_directory(
        app.config["MAQOLA_PAPKA"], maqola["fayl_nomi"],
        as_attachment=True, download_name=maqola["original_nomi"],
    )


@app.errorhandler(RequestEntityTooLarge)
def fayl_katta(e):
    til = g.get("til", config.ASOSIY_TIL)
    messages = {
        "uz": "Yuborilgan forma yoki fayl hajmi ruxsat etilgan chegaradan oshdi. Hajmni kamaytirib, qayta yuboring.",
        "en": "The submitted form or file exceeds the allowed size. Reduce its size and try again.",
        "tr": "Gönderilen form veya dosya izin verilen boyutu aşıyor. Boyutu küçültüp tekrar deneyin.",
    }
    return render_template("xato.html", kod=413, xabar=messages[til]), 413


# --- Admin panel -----------------------------------------------------------

@app.route("/admin/kirish", methods=["GET", "POST"])
def admin_kirish():
    if request.method == "POST":
        enforce_rate("login", 5, 900)
        if not app.config["ADMIN_PAROL"] and not app.config["ADMIN_PASSWORD_HASH"]:
            return render_template("xato.html", kod=503, xabar=config.MATN[g.til]["admin_unconfigured"]), 503
        login = request.form.get("login", "")
        parol = request.form.get("parol", "")
        password_hash = app.config["ADMIN_PASSWORD_HASH"]
        password_ok = (check_password_hash(password_hash, parol) if password_hash else
                       hmac.compare_digest(parol.encode(), app.config["ADMIN_PAROL"].encode()))
        if hmac.compare_digest(login.encode(), app.config["ADMIN_LOGIN"].encode()) and password_ok:
            session.clear()
            session.permanent = True
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        flash("Login yoki parol noto'g'ri.", "xato")
    return render_template("admin_kirish.html")


@app.route("/admin/chiqish", methods=["POST"])
def admin_chiqish():
    session.clear()
    return redirect(url_for("bosh_sahifa"))


@app.route("/admin")
@admin_kerak
def admin_panel():
    faqat_yangi = request.args.get("holat") == "yangi"
    search = request.args.get("q", "").strip()[:100]
    status = request.args.get("maqola_holat", "")
    if status not in models.HOLATLAR:
        status = ""
    messages = models.paginated("messages", request.args.get("xpage", 1, type=int), search, unread=faqat_yangi)
    papers = models.paginated("papers", request.args.get("mpage", 1, type=int), search, status)
    return render_template("admin.html", xabarlar=messages["rows"], stat=models.statistika(),
        faqat_yangi=faqat_yangi, maqolalar=papers["rows"], messages=messages, papers=papers,
        search=search, status=status)


@app.route("/admin/maqola/<int:maqola_id>/yuklab-olish")
@admin_kerak
def admin_maqola_yuklab_olish(maqola_id):
    maqola = models.maqola_topish(maqola_id)
    if maqola is None:
        return redirect(url_for("admin_panel"))
    return maqola_javobi(maqola)


@app.route("/admin/maqola/<int:maqola_id>/tasdiqlash", methods=["POST"])
@admin_kerak
def admin_maqola_tasdiqlash(maqola_id):
    if models.maqola_topish(maqola_id) is None:
        abort(404)
    models.maqola_tasdiqlash(maqola_id)
    flash("Maqola tasdiqlandi va saytda ko'rina boshladi.", "muvaffaqiyat")
    return redirect(url_for("admin_panel"))


@app.route("/admin/maqola/<int:maqola_id>/ochirish", methods=["POST"])
@admin_kerak
def admin_maqola_ochirish(maqola_id):
    maqola = models.maqola_topish(maqola_id)
    if maqola is not None:
        fayl_yoli = os.path.join(app.config["MAQOLA_PAPKA"], maqola["fayl_nomi"])
        if not app.config.get("DATABASE_URL") and os.path.exists(fayl_yoli):
            os.remove(fayl_yoli)
        models.maqola_ochirish(maqola_id)
        flash("Maqola o'chirildi.", "muvaffaqiyat")
    return redirect(url_for("admin_panel"))


@app.route("/admin/oqildi/<int:xabar_id>", methods=["POST"])
@admin_kerak
def admin_oqildi(xabar_id):
    models.xabar_oqildi(xabar_id)
    return redirect(url_for("admin_panel"))


@app.route("/admin/ochirish/<int:xabar_id>", methods=["POST"])
@admin_kerak
def admin_ochirish(xabar_id):
    models.xabar_ochirish(xabar_id)
    flash("Xabar o'chirildi.", "muvaffaqiyat")
    return redirect(url_for("admin_panel"))


@app.route("/admin/eksport")
@admin_kerak
def admin_eksport():
    """Aloqa xabarlarini CSV ko'rinishida yuklab beradi."""
    chiqish = io.StringIO()
    yozuvchi = csv.writer(chiqish)
    yozuvchi.writerow(["ID", "Ism", "Email", "Mavzu", "Xabar", "Til", "Sana"])
    for q in models.xabarlar_royxati():
        values = [q["id"], q["ism"], q["email"], q["mavzu"], q["xabar"], q["til"], q["yaratilgan"]]
        yozuvchi.writerow([csv_safe(value) for value in values])

    return Response(
        # Excel UTF-8'ni to'g'ri o'qishi uchun BOM qo'shamiz
        "﻿" + chiqish.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=xabarlar.csv"},
    )


# --- Xatoliklar ------------------------------------------------------------

@app.errorhandler(404)
def sahifa_topilmadi(e):
    til = g.get("til", config.ASOSIY_TIL)
    return render_template("xato.html", kod=404,
                           xabar=config.MATN[til]["xato_404"]), 404


@app.errorhandler(500)
def server_xatosi(e):
    til = g.get("til", config.ASOSIY_TIL)
    return render_template("xato.html", kod=500,
                           xabar=config.MATN[til]["xato_500"]), 500


@app.route("/royxatdan-otish", defaults={"til": config.ASOSIY_TIL}, methods=["GET", "POST"])
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/royxatdan-otish", methods=["GET", "POST"])
def royxatdan_otish():
    opened = app.config["REGISTRATION_OPEN"] and datetime.now(timezone.utc) < datetime.fromisoformat(config.SANA_ISO)
    form, error = {}, ""
    if request.method == "POST":
        if not opened:
            return render_template("registration.html", opened=False, form={}, error=""), 403
        enforce_rate("registration", 5, 600)
        form = {key: request.form.get(key, "").strip() for key in ("ism", "email", "tashkilot", "format")}
        form["email"] = form["email"].lower()
        if (not 2 <= len(form["ism"]) <= 150 or not email_togrimi(form["email"])
                or not 2 <= len(form["tashkilot"]) <= 200 or form["format"] not in ("in_person", "online")
                or request.form.get("consent") != "yes"):
            error = config.MATN[g.til]["registration_error"]
            return render_template("registration.html", opened=opened, form=form, error=error), 422
        models.qatnashchi_qoshish(form["ism"], form["email"], form["tashkilot"], form["format"], g.til)
        # Same response for an existing email; do not disclose registrations.
        flash(config.MATN[g.til]["registration_success"], "muvaffaqiyat")
        return redirect(url_for("royxatdan_otish"))
    return render_template("registration.html", opened=opened, form=form, error=error)


@app.route("/admin/qatnashchilar")
@admin_kerak
def admin_qatnashchilar():
    search = request.args.get("q", "").strip()[:100]
    listing = models.paginated("participants", request.args.get("page", 1, type=int), search)
    return render_template("participants.html", listing=listing, search=search)


def csv_safe(value):
    text = str(value or "")
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")) else value


@app.route("/admin/maqola/<int:maqola_id>/holat", methods=["POST"])
@admin_kerak
def admin_maqola_holat(maqola_id):
    paper = models.maqola_topish(maqola_id)
    if paper is None:
        abort(404)
    status = request.form.get("holat", "")
    note = request.form.get("izoh", "").strip()
    if status not in models.HOLATLAR or len(note) > 3000:
        abort(400)
    changed = status != paper["holat"] or note != (paper["izoh"] or "")
    models.maqola_holatini_ozgartirish(maqola_id, status, note)
    if changed and app.config["SMTP_HOST"]:
        paper = models.maqola_topish(maqola_id)
        if not notify_author(paper, tracking_url(paper), config.MATN[paper["til"]]):
            flash(config.MATN[g.til]["mail_failed"], "xato")
    flash("Maqola holati saqlandi.", "muvaffaqiyat")
    return redirect(url_for("admin_panel"))


@app.errorhandler(CSRFError)
def csrf_error(error):
    return render_template("xato.html", kod=400, xabar=config.MATN[g.get("til", "uz")]["csrf_error"]), 400


@app.after_request
def secure_response(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    if (request.path.startswith("/admin") or "maqola-holati/" in request.path
            or request.endpoint == "maqola_yuklab_olish"):
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        response.headers["Referrer-Policy"] = "no-referrer"
    elif response.mimetype == "text/html":
        # Forms include session-specific CSRF tokens.
        response.headers["Cache-Control"] = "no-cache, private"
    if request.is_secure:
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


@app.route("/taqvim.ics", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/taqvim.ics")
def taqvim():
    def escape(value):
        return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    event = config.KONFERENSIYA[g.til]
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//TYM//Conference 2026//UZ", "CALSCALE:GREGORIAN",
             "BEGIN:VEVENT", "UID:tym-2026-12-15@conference", "DTSTAMP:20260101T000000Z",
             "DTSTART;VALUE=DATE:20261215", "DTEND;VALUE=DATE:20261217",
             "SUMMARY:" + escape(event["nom"]), "LOCATION:" + escape(event["manzil"]), "END:VEVENT", "END:VCALENDAR"]
    # RFC 5545 folds lines at 75 octets without splitting UTF-8 characters.
    folded = []
    for line in lines:
        part = ""
        for char in line:
            if len((part + char).encode("utf-8")) > 75:
                folded.append(part)
                part = " "
            part += char
        folded.append(part)
    return Response("\r\n".join(folded) + "\r\n", mimetype="text/calendar",
                    headers={"Content-Disposition": "attachment; filename=conference-2026.ics"})


@app.route("/dastur", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/dastur")
def dastur():
    return render_template("dastur.html", faol="dastur")


@app.route("/maxfiylik", defaults={"til": config.ASOSIY_TIL})
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/maxfiylik")
def maxfiylik():
    return render_template("maxfiylik.html", faol="maxfiylik")


@app.route("/sitemap.xml")
def sitemap():
    root = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    origin = app.config["PUBLIC_URL"] or request.url_root.rstrip("/")
    for language in config.TILLAR:
        for endpoint in ("bosh_sahifa", "haqida", "yonalishlar", "kengash", "talablar",
                         "aloqa", "maqolalar_royxati", "royxatdan_otish", "dastur", "maxfiylik"):
            SubElement(SubElement(root, "url"), "loc").text = origin + url_for(endpoint, til=language)
    return Response(tostring(root, encoding="utf-8", xml_declaration=True), mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    origin = app.config["PUBLIC_URL"] or request.url_root.rstrip("/")
    lines = ["User-agent: *", "Disallow: /admin", "Disallow: /maqola/"]
    for prefix in ("", "/en", "/tr"):
        lines.append(f"Disallow: {prefix}/maqola-holati/")
    lines.append(f"Sitemap: {origin}/sitemap.xml")
    return Response("\n".join(lines) + "\n", mimetype="text/plain")


models.init_db(app)

if __name__ == "__main__":
    # Tuzatish rejimi (debug) faqat shu mashinada ishlaganda yoqiladi.
    # U yoqilganda xatolik sahifasida interaktiv konsol ochiladi — o'sha
    # konsol orqali serverda buyruq bajarsa bo'ladi. Shuning uchun sayt
    # tashqariga chiqarilganda DEBUG hech qachon yoqilmasligi kerak.
    debug = os.environ.get("DEBUG", "0") == "1"
    app.run(debug=debug, host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)))
