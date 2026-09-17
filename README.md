# Turkiy yozma meros — 2026

«Turkiy yozma meros: sivilizatsiyalararo muloqot va raqamli kelajak» xalqaro
ilmiy yig'ini sayti. Flask + Jinja2 + SQLite, tashqi kutubxonalarsiz (faqat Flask).

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

**Maqola yuborish formasi yo'q** — chorlovga ko'ra maqolalar elektron pochta
(`mangu8bitig@gmail.com`) orqali qabul qilinadi. Saytdagi «Maqola yuborish»
tugmasi shu pochtani ochadi.

## Matnlarni o'zgartirish

Barcha matn — konferensiya nomi, sanasi, yo'nalishlar, ekspertlar, talablar —
`config.py` faylida, har biri uch tilda. Shablonlarga tegmasdan shu faylni
tahrirlash kifoya. `SANA_ISO` bosh sahifadagi teskari hisoblagichni boshqaradi.

## Ekspertlar rasmlari

`static/img/ekspertlar/` papkasiga qo'yiladi, fayl nomi `config.py` dagi `rasm`
maydoniga mos bo'lishi kerak (ro'yxat: `static/img/ekspertlar/README.md`).
Rasm qo'yilmagan bo'lsa sayt ism bosh harflaridan avatar chizadi — buzilmaydi.

## Admin panel

<http://127.0.0.1:5000/admin/kirish> — standart login `admin`, parol `admin123`.
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
