# Turkiy yozma meros — 2026

«Turkiy yozma meros: sivilizatsiyalararo muloqot va raqamli kelajak» xalqaro
ilmiy yig'ini sayti. Flask + Jinja2, lokal SQLite yoki PostgreSQL; hujjatlar tuzilishini tekshirish va CSRF himoyasi bilan.

**Yig'in:** 2026-yil 15–16-dekabr · Toshkent davlat sharqshunoslik universiteti
**Tashkilotchilar:** OTFIV · TDSHU · Turkiy Davlatlar Tashkiloti (TDT) · Turk Tili Qurumi (TDK)

Barcha ma'lumot tashkiliy qo'mita tarqatgan chorlovdan olingan
(`static/chorlov/` ichida uchta tildagi asl PDF turibdi).

## Ishga tushirish

```bash
cd /mnt/c/Users/Sarvarbek/projects/konferensiya
pip install -r requirements.txt
python3 app.py
```

Sayt: <http://127.0.0.1:5000> — baza (`data/konferensiya.db`) birinchi ishga
tushirishda avtomatik yaratiladi.

## Uch til

Sayt to'liq uch tilda: **o'zbek, ingliz, turk**. Til manzil prefiksi bilan
tanlanadi, o'zbekchada prefiks yo'q:

| Til | Manzil |
|---|---|
| O'zbekcha | `/`, `/haqida`, `/kengash` … |
| English | `/en/`, `/en/haqida`, `/en/kengash` … |
| Türkçe | `/tr/`, `/tr/haqida`, `/tr/kengash` … |

Sarlavhadagi UZ / EN / TR tugmalari **ayni shu sahifaning** boshqa tildagi
nusxasiga olib boradi.

## Sahifalar

| Manzil | Nima |
|---|---|
| `/` | Bosh sahifa — chorlov, teskari hisoblagich, muhim sanalar, yo'nalishlar, ekspertlar |
| `/haqida` | Yig'in maqsadi, tashkilotchilar, umumiy ma'lumot, chorlov PDF |
| `/yonalishlar` | Beshta ilmiy yo'nalish (kengash) |
| `/kengash` | Ilmiy kengash — xalqaro va mahalliy ekspertlar, rasm va lavozimi bilan |
| `/talablar` | Maqola talablari + maqola qayerga yuboriladi |
| `/aloqa` | Aloqa formasi va tashkiliy qo'mita manzili |
| `/admin` | Kelgan aloqa xabarlari (login talab qiladi) |

Maqolalar `/talablar#yuborish` formasi orqali PDF/DOC/DOCX formatida yoki
ko'rsatilgan elektron pochta orqali qabul qilinadi. Saytga yuborilgan maqola
maxfiy kuzatuv havolasini oladi; faqat admin tasdiqlagach ommaga ochiladi.
`/royxatdan-otish` orqali qatnashchi sifatida ro'yxatdan o'tish mumkin.
`/taqvim.ics` konferensiyani taqvimga qo'shadi.

## Matnlarni o'zgartirish

Barcha matn — konferensiya nomi, sanasi, yo'nalishlar, ekspertlar, talablar —
`config.py` faylida, har biri uch tilda. Shablonlarga tegmasdan shu faylni
tahrirlash kifoya. `SANA_ISO` bosh sahifadagi teskari hisoblagichni boshqaradi.

## Ekspertlar rasmlari

`static/img/ekspertlar/` papkasiga qo'yiladi, fayl nomi `config.py` dagi `rasm`
maydoniga mos bo'lishi kerak (ro'yxat: `static/img/ekspertlar/README.md`).
Rasm qo'yilmagan bo'lsa sayt ism bosh harflaridan avatar chizadi — buzilmaydi.

## Admin panel

<http://127.0.0.1:5000/admin/kirish> — login `ADMIN_LOGIN` (sukut bo'yicha `admin`).
Standart parol yo'q: `ADMIN_PAROL` yoki `ADMIN_PASSWORD_HASH` sozlanmasa kirish yopiq.
Kelgan aloqa xabarlarini ko'rish, o'qilgan deb belgilash, o'chirish va CSV'ga
eksport qilish.

Ishlab chiqarishda albatta o'zgartiring:

```bash
export SECRET_KEY="uzun-tasodifiy-kalit"
export ADMIN_LOGIN="..." ADMIN_PAROL="..."
```

## Tuzilma

```
app.py             — yo'llar + til qatlami (url prefiksi orqali uz/en/tr)
config.py          — sozlamalar + uch tildagi barcha matn va ma'lumot
models.py          — sqlite3: aloqa xabarlari
templates/         — Jinja2 shablonlari (base.html asos, qismlar/ — bo'laklar)
static/css/        — style.css
static/js/         — main.js (menyu, hisoblagich, flash)
static/img/        — nishon va ekspertlar rasmlari
static/chorlov/    — chorlovning uchta tildagi asl PDF fayli
data/              — SQLite bazasi
```

## Ishlab chiqarishga chiqarish

`python3 app.py` faqat ishlab chiqish uchun. Server uchun:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Vercel va Supabase

Vercel Flask ilovasini `app.py` orqali aniqlaydi. Environment Variables ichida
`DATABASE_URL` (Supabase Transaction pooler PostgreSQL URI), `SECRET_KEY`,
`ADMIN_LOGIN`, `ADMIN_PAROL` ni belgilang. URI parolida maxsus belgilar bo'lsa,
ular URL encoding bilan yozilishi kerak. Muhit o'zgaruvchilari o'zgargach yangi
deploy kerak.

`DATABASE_URL` mavjud bo'lsa xabarlar, maqola ma'lumotlari va fayl baytlari
PostgreSQL'da saqlanadi; jadvallar avtomatik yaratiladi. Supabase Data API'da
jadvallarga anonim kirish RLS bilan yopiladi. Fayllar faqat admin yoki maqola
tasdiqlangandan keyin ochiq yuklab olish yo'li orqali olinadi.
Maqola fayli chegarasi sukut bo'yicha **50 MB** (50 × 1024 × 1024 bayt).
`MAX_UPLOAD_MB=100` kabi muhit o'zgaruvchisi bilan uni oshirish mumkin.
Forma maydonlari uchun so'rov chegarasida qo'shimcha 1 MiB joy ajratiladi.
Reverse proxy ishlatilsa, uning so'rov chegarasini ham moslang
(masalan, Nginx uchun 50 MB faylga `client_max_body_size 51m;`).
Vercel Functions so'rov va javob hajmini 4,5 MB bilan cheklaydi; ilova
sozlamasi bu platforma chegarasini oshirmaydi. Vercelda katta fayllar uchun
brauzerdan bevosita object storage'ga yuklash/yuklab olishni joriy qilish
yoki Flask ilovasini katta so'rovlarni qo'llaydigan serverga joylash kerak.
Lokal muhitda DATABASE_URL bo'lmasa SQLite va lokal fayllar ishlaydi.
Mavjud PythonAnywhere/SQLite ma'lumotlari avtomatik ko'chirilmaydi.

## Xavfsizlik va yangi imkoniyatlar

- Har bir POST forma CSRF token bilan himoyalangan; logout ham POST.
- Login: 15 daqiqada 5 urinish; aloqa, maqola va ro'yxatdan o'tish: har biri
  10 daqiqada 5 urinish / IP. Cheklov bazada saqlanadi, workerlar o'rtasida umumiy.
- `APP_ENV=production` yoki Vercelda kamida 32 belgili `SECRET_KEY` majburiy.
  Lokal muhitda kalit `data/.session-key` da saqlanadi va Git'ga kiritilmaydi.
- Ishlab chiqarishda `COOKIE_SECURE=1` va HTTPS ishlating. Debug sukut bo'yicha o'chiq.
- Ishonchli reverse proxy bo'lsa `TRUSTED_PROXY_HOPS` ni shu infratuzilmadagi
  haqiqiy proxy soniga moslang. Bevosita internetga ochilgan serverda `0` qolsin.
- Admin panel: qidiruv, holat filtri, 20 tadan sahifalash, izoh va holatni o'zgartirish.
  Tasdiq bekor qilinsa yuklab olish darhol yopiladi. Qatnashchilar ro'yxati admin uchungina.
- `SUBMISSIONS_OPEN=0` maqola qabulini, `REGISTRATION_OPEN=0` qatnashchi qabulini yopadi.
  Maqola muddati Toshkent vaqti bilan avtomatik tekshiriladi.
- Bir emaildan bir xil fayl takroran saqlanmaydi. Eski maqolalar saqlanadi;
  eski yozuvlarga kuzatuv havolasi avtomatik berilmaydi.
- Fayl tuzilishini tekshirish antivirus tekshiruvi o'rnini bosmaydi.

### Email xabarnomalari (ixtiyoriy)

`SMTP_HOST`, `SMTP_PORT` (587), `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
va `PUBLIC_URL=https://sizning-domeningiz` ni sozlang. 465-port uchun `SMTP_SSL=1`.
Boshqa holatda STARTTLS majburiy ishlatiladi. Sozlamalar bo'lmasa tarmoq orqali
xat yuborilmaydi; foydalanuvchi kuzatuv havolasini sahifadan saqlab oladi.
SMTP xatosi maqolani saqlashni bekor qilmaydi. Maxfiy havolani boshqalarga bermang.

### Tekshirish

```bash
python -m unittest discover -s tests -v
```

Testlar alohida vaqtinchalik SQLite bazasida ishlaydi, haqiqiy ma'lumotlarga tegmaydi.
Ishga tushirishdan avval `pip install -r requirements.txt` bajarilishi kerak.
