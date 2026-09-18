# -*- coding: utf-8 -*-
"""Konferensiya sayti uchun sozlamalar va uch tildagi barcha matnlar.

Manba: tashkiliy qo'mita tarqatgan chorlov (Uzbek/Turk/English PDF).
Saytdagi biror matnni o'zgartirish uchun faqat shu faylni tahrirlash kifoya —
shablonlarga tegilmaydi.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "turkiy-yozma-meros-2026")

    DATABASE = os.path.join(BASE_DIR, "data", "konferensiya.db")
    MAQOLA_PAPKA = os.path.join(BASE_DIR, "data", "maqolalar")
    MAQOLA_KENGAYTMALAR = {"pdf", "doc", "docx"}
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB

    ADMIN_LOGIN = os.environ.get("ADMIN_LOGIN", "admin")
    ADMIN_PAROL = os.environ.get("ADMIN_PAROL", "admin123")

    # Shablonlar o'zgarsa serverni qayta ishga tushirmasdan yangilansin.
    # DEBUG o'chiq bo'lganda Flask sukut bo'yicha ularni keshlab qo'yadi;
    # sayt kichkina, tekshiruv qiymati arzon.
    TEMPLATES_AUTO_RELOAD = True


# ---------------------------------------------------------------------------
# Tillar
# ---------------------------------------------------------------------------

TILLAR = {
    "uz": {"nom": "O'zbekcha", "qisqa": "UZ", "html": "uz"},
    "en": {"nom": "English", "qisqa": "EN", "html": "en"},
    "tr": {"nom": "Türkçe", "qisqa": "TR", "html": "tr"},
}
ASOSIY_TIL = "uz"


# ---------------------------------------------------------------------------
# Tildan qat'i nazar bir xil bo'lgan ma'lumotlar
# ---------------------------------------------------------------------------

ALOQA = {
    "email": "mangu8bitig@gmail.com",
    "telefon": "+998 90 965 86 56",
    "telefon_raqam": "+998909658656",
    "telegram": "https://t.me/+998909658656",
    "whatsapp": "https://wa.me/998909658656",
}

# Bosh sahifadagi teskari hisoblagich shu sanaga qarab ishlaydi
SANA_ISO = "2026-12-15T09:00:00"
MUDDAT_ISO = "2026-11-15T23:59:59"


# ---------------------------------------------------------------------------
# Konferensiya — asosiy ma'lumotlar, uch tilda
# ---------------------------------------------------------------------------

KONFERENSIYA = {
    "uz": {
        "nom": "Turkiy yozma meros: sivilizatsiyalararo muloqot va raqamli kelajak",
        "qisqa_nom": "Turkiy yozma meros — 2026",
        "belgi": "TYM 2026",
        "tur": "Xalqaro ilmiy yig'in",
        "bagishlov": "«Butunjahon turkiy tillar oilasi kuni»ga bag'ishlanadi",
        "shior": "Dunyo qo'lyozma fondlaridagi turkiy yodgorliklarni "
                 "o'rganish, raqamlashtirish va jahon ilmiga tanitish",
        "sana": "2026-yil 15–16-dekabr",
        "sana_qisqa": "15–16.12.2026",
        "joy": "Toshkent davlat sharqshunoslik universiteti",
        "manzil": "Toshkent, Amir Temur ko'chasi, 20-uy",
        "format": "Aralash: jonli va ZOOM platformasi orqali",
        "tillar_royxati": "O'zbek, turk, ingliz, rus",
        "muddat": "2026-yil 15-noyabr",
    },
    "en": {
        "nom": "Turkic Written Heritage: Intercivilizational Dialogue and the Digital Future",
        "qisqa_nom": "Turkic Written Heritage 2026",
        "belgi": "TWH 2026",
        "tur": "International Scientific Conference",
        "bagishlov": "Dedicated to World Turkic Languages Family Day",
        "shior": "Studying, digitizing and promoting Turkic written monuments "
                 "preserved in manuscript collections worldwide",
        "sana": "December 15–16, 2026",
        "sana_qisqa": "15–16 Dec 2026",
        "joy": "Tashkent State University of Oriental Studies",
        "manzil": "20 Amir Temur Street, Tashkent, Uzbekistan",
        "format": "Hybrid: in-person and via the ZOOM platform",
        "tillar_royxati": "Uzbek, Turkish, English, Russian",
        "muddat": "November 15, 2026",
    },
    "tr": {
        "nom": "Türk Yazılı Mirası: Medeniyetler Arası Diyalog ve Dijital Gelecek",
        "qisqa_nom": "Türk Yazılı Mirası 2026",
        "belgi": "TYM 2026",
        "tur": "Uluslararası Sempozyum",
        "bagishlov": "«Dünya Türk Dili Ailesi Günü» münasebetiyle düzenlenmektedir",
        "shior": "Dünya el yazması fonlarında muhafaza edilen Türk yazılı "
                 "eserlerini incelemek, dijitalleştirmek ve dünyaya tanıtmak",
        "sana": "15–16 Aralık 2026",
        "sana_qisqa": "15–16.12.2026",
        "joy": "Taşkent Devlet Şarkiyat Üniversitesi",
        "manzil": "Emir Timur Caddesi No 20, Taşkent",
        "format": "Karma: yüz yüze ve ZOOM platformu üzerinden",
        "tillar_royxati": "Özbekçe, Türkçe, İngilizce, Rusça",
        "muddat": "15 Kasım 2026",
    },
}


# ---------------------------------------------------------------------------
# Tashkilotchilar
# ---------------------------------------------------------------------------

TASHKILOTCHILAR = {
    "uz": [
        "O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi",
        "Toshkent davlat sharqshunoslik universiteti",
        "Turkiy Davlatlar Tashkiloti (TDT)",
        "Turk Tili Qurumi (TDK)",
    ],
    "en": [
        "Ministry of Higher Education, Science and Innovation of the Republic of Uzbekistan",
        "Tashkent State University of Oriental Studies",
        "Organization of Turkic States (OTS)",
        "Turkish Language Association (TDK)",
    ],
    "tr": [
        "Özbekistan Cumhuriyeti Yükseköğretim, Bilim ve İnovasyon Bakanlığı",
        "Taşkent Devlet Şarkiyat Üniversitesi",
        "Türk Devletleri Teşkilatı (TDT)",
        "Türkiye Cumhuriyeti Türk Dil Kurumu (TDK)",
    ],
}


# ---------------------------------------------------------------------------
# Yig'inning maqsadlari (chorlovdan)
# ---------------------------------------------------------------------------

MAQSADLAR = {
    "uz": [
        "dunyo qo'lyozma fondlarida saqlanayotgan turkiy yozma yodgorliklarni "
        "tarix, filologiya va matnshunoslik yo'nalishlarida o'rganish",
        "ushbu sohalarda raqamlashtirishni kuchaytirish",
        "sun'iy intellekt tizimlaridan unumli foydalanish",
        "yozma yodgorliklarda qo'llangan so'z boyligining elektron korpuslarini yaratish",
        "turkiy xalqlar yozma merosini dunyo ilmida targ'ib qilish",
    ],
    "en": [
        "study Turkic written monuments preserved in manuscript collections around "
        "the world from the perspectives of history, philology and textual studies",
        "strengthen digitalization in these fields",
        "make effective use of artificial intelligence technologies",
        "create electronic corpora of the vocabulary used in written monuments",
        "promote the written heritage of the Turkic peoples in the international "
        "academic community",
    ],
    "tr": [
        "dünya el yazması fonlarında muhafaza edilen Türk yazılı eserlerini tarih, "
        "filoloji ve metin neşri / eleştirisi alanlarında incelemek",
        "bu alanlarda dijitalleşmeyi güçlendirmek",
        "yapay zekâ uygulamalarından etkin bir şekilde yararlanmak",
        "yazılı eserlerde kullanılan kelime hazinesinin elektronik korpuslarını oluşturmak",
        "Türk halklarının yazılı mirasını dünya bilim dünyasında tanıtmak",
    ],
}


# ---------------------------------------------------------------------------
# Ilmiy yig'in kengashlari — 5 ta yo'nalish
# ---------------------------------------------------------------------------

YONALISHLAR = [
    {
        "id": 1,
        "raqam": "I",
        "uz": {
            "nom": "Turkiy yozma yodgorliklarni qiyosiy-tarixiy o'rganish",
            "tavsif": "Qadimgi turkiy bitiglarning tili, uslubi va poetikasi.",
        },
        "en": {
            "nom": "Comparative-Historical Study of Turkic Written Monuments",
            "tavsif": "The language, style and poetics of Old Turkic inscriptions.",
        },
        "tr": {
            "nom": "Türk Yazılı Eserlerinin Karşılaştırmalı-Tarihî İncelemesi",
            "tavsif": "Eski Türk yazıtlarının dili, üslubu ve poetiği.",
        },
    },
    {
        "id": 2,
        "raqam": "II",
        "uz": {
            "nom": "Manbashunoslik va matnshunoslik masalalari",
            "tavsif": "Qo'lyozmalar va epigrafik yodgorliklarning tanqidiy matnini "
                      "tayyorlash va paleografik tahlil muammolari.",
        },
        "en": {
            "nom": "Source Studies and Textual Criticism",
            "tavsif": "Problems of preparing critical editions and conducting "
                      "paleographic analyses of manuscripts and epigraphic monuments.",
        },
        "tr": {
            "nom": "Kaynak Kodlaması ve Metin Neşri Meseleleri",
            "tavsif": "El yazmalarının ve epigrafik eserlerin tenkitli metnini "
                      "hazırlama ile paleografik analiz sorunları.",
        },
    },
    {
        "id": 3,
        "raqam": "III",
        "uz": {
            "nom": "Kompyuter tilshunosligi va elektron korpuslar",
            "tavsif": "Turkiy tillarning milliy va tarixiy elektron korpuslarini "
                      "yaratish tajribasi.",
        },
        "en": {
            "nom": "Computational Linguistics and Electronic Corpora",
            "tavsif": "Experiences in creating national and historical electronic "
                      "corpora of Turkic languages.",
        },
        "tr": {
            "nom": "Bilgisayarlı Dil Bilimi ve Elektronik Korpuslar",
            "tavsif": "Türk dillerinin millî ve tarihî elektronik korpuslarını "
                      "oluşturma deneyimleri.",
        },
    },
    {
        "id": 4,
        "raqam": "IV",
        "uz": {
            "nom": "Raqamlashtirish va innovatsiyalar",
            "tavsif": "Sun'iy intellekt (AI) va OCR texnologiyalarini qadimiy turkiy "
                      "matnlarni deshifrovka va restavratsiya qilishdagi tatbiqi.",
        },
        "en": {
            "nom": "Digitalization and Innovations",
            "tavsif": "Applications of Artificial Intelligence (AI) and OCR "
                      "technologies in the decipherment and restoration of ancient "
                      "Turkic texts.",
        },
        "tr": {
            "nom": "Dijitalleştirme ve İnovasyon",
            "tavsif": "Yapay zekâ (AI) ve OCR teknolojilerinin eski Türkçe metinlerin "
                      "çözümlenmesi ve restorasyonundaki uygulamaları.",
        },
    },
    {
        "id": 5,
        "raqam": "V",
        "uz": {
            "nom": "Muzeylashtirish va global integratsiya",
            "tavsif": "Turkiy yozma merosni saqlashda xalqaro kutubxonalararo "
                      "tarmoqlarni yaratish va madaniy turizmni rivojlantirish.",
        },
        "en": {
            "nom": "Musealization and Global Integration",
            "tavsif": "Establishing international interlibrary networks for the "
                      "preservation of Turkic written heritage and developing "
                      "cultural tourism.",
        },
        "tr": {
            "nom": "Müzeleşme ve Küresel Entegrasyon",
            "tavsif": "Türk yazılı mirasının korunmasında uluslararası kütüphaneler "
                      "arası ağların kurulması ve kültürel turizmin geliştirilmesi.",
        },
    },
]


# ---------------------------------------------------------------------------
# Ilmiy kengash a'zolari
#
# `rasm` — static/img/ekspertlar/ ichidagi fayl nomi. Fayl bo'lmasa sayt
# ism bosh harflaridan avtomatik avatar chizadi, shuning uchun rasmni
# keyinroq qo'shsa ham sayt buzilmaydi.
# ---------------------------------------------------------------------------

XALQARO_KENGASH = [
    {
        "ism": "Elçin İbrahimov",
        "harf": "Eİ",
        "rasm": "elcin-ibrahimov.jpg",
        "havola": "https://az.wikipedia.org/wiki/El%C3%A7in_%C4%B0brahimov",
        "uz": {"unvon": "Dotsent, doktor", "tashkilot": "Turkiy tillar tadqiqotchisi", "mamlakat": "Ozarbayjon"},
        "en": {"unvon": "Assoc. Prof., PhD", "tashkilot": "Researcher of Turkic languages", "mamlakat": "Azerbaijan"},
        "tr": {"unvon": "Doç. Dr.", "tashkilot": "Türk dilleri araştırmacısı", "mamlakat": "Azerbaycan"},
    },
    {
        "ism": "Saıdbek Boltabayev",
        "harf": "SB",
        "rasm": "saidbek-boltabayev.jpg",
        "havola": "https://unis.karabuk.edu.tr/akademisyen/sboltabayev",
        "uz": {
            "unvon": "Dots. dr.",
            "tashkilot": "Karabuk universiteti — Inson va jamiyat fanlari fakulteti, "
                         "Turk tili va adabiyoti bo'limi, Qadimgi turkiy til kafedrasi",
            "mamlakat": "Turkiya",
        },
        "en": {
            "unvon": "Assoc. Prof. Dr.",
            "tashkilot": "Karabük University — Faculty of Humanities and Social Sciences, "
                         "Department of Turkish Language and Literature, Old Turkic Language",
            "mamlakat": "Türkiye",
        },
        "tr": {
            "unvon": "Doç. Dr.",
            "tashkilot": "Karabük Üniversitesi — İnsan ve Toplum Bilimleri Fakültesi, "
                         "Türk Dili ve Edebiyatı Bölümü, Eski Türk Dili Anabilim Dalı",
            "mamlakat": "Türkiye",
        },
    },
    {
        "ism": "Mamura Mamatkulova Özkan",
        "harf": "MM",
        "rasm": "mamura-mamatkulova.jpg",
        "havola": "https://avesis.istanbul.edu.tr/mamura.mamatkulova",
        "uz": {"unvon": "O'qit. dr.", "tashkilot": "Istanbul universiteti", "mamlakat": "Turkiya"},
        "en": {"unvon": "Lecturer, PhD", "tashkilot": "Istanbul University", "mamlakat": "Türkiye"},
        "tr": {"unvon": "Öğr. Gör. Dr.", "tashkilot": "İstanbul Üniversitesi", "mamlakat": "Türkiye"},
    },
    {
        "ism": "Veli Savaş",
        "harf": "VS",
        "rasm": "veli-savas.jpg",
        "havola": "",
        "uz": {"unvon": "Professor", "tashkilot": "Turk Tili Qurumi (TDK)", "mamlakat": "Turkiya"},
        "en": {"unvon": "Professor", "tashkilot": "Turkish Language Association (TDK)", "mamlakat": "Türkiye"},
        "tr": {"unvon": "Prof.", "tashkilot": "Türk Dil Kurumu (TDK)", "mamlakat": "Türkiye"},
    },
    {
        "ism": "Tsendiin Battulga",
        "harf": "TB",
        "rasm": "tsendiin-battulga.jpg",
        "havola": "",
        "uz": {
            "unvon": "Professor, doktor",
            "tashkilot": "Mo'g'uliston Milliy universiteti — qadimgi turkiy tillar, "
                         "run bitiklari va qadimiy yozuvlar mutaxassisi",
            "mamlakat": "Mo'g'uliston",
        },
        "en": {
            "unvon": "Professor, Dr.",
            "tashkilot": "National University of Mongolia — specialist in Old Turkic "
                         "languages, runic inscriptions and ancient scripts",
            "mamlakat": "Mongolia",
        },
        "tr": {
            "unvon": "Prof. Dr.",
            "tashkilot": "Moğolistan Millî Üniversitesi — Eski Türk dilleri, runik "
                         "yazıtlar ve eski yazılar uzmanı",
            "mamlakat": "Moğolistan",
        },
    },
]

# Quyidagi ikki surat Vikiomborda CC BY-SA 4.0 shartlari bilan e'lon qilingan.
# Litsenziya muallifni ko'rsatishni talab qiladi — «Ilmiy kengash» sahifasining
# etagida chiqadi. Tashkilotchilardan rasmiy suratlar kelgach, bu ro'yxat
# bo'shatiladi va suratlar shunchaki almashtiriladi.
# Bosh sahifadagi qahramon surati — Kultegin bitigtoshi (Vikiombor, CC BY-SA 4.0).
QAHRAMON_SURAT = {
    "tavsif": "Kultegin bitigtoshi — Urxun bitiklari",
    "muallif": "Vezirtonyukuk",
    "litsenziya": "CC BY-SA 4.0",
    "havola": "https://commons.wikimedia.org/wiki/File:Kultigin_Monument_of_Orkhon_Inscriptions.jpeg",
}

RASM_MANBALARI = [
    {
        "ism": "Gulchehra Rixsiyeva",
        "muallif": "Hulkar Vosilovna",
        "litsenziya": "CC BY-SA 4.0",
        "havola": "https://commons.wikimedia.org/wiki/File:Rixsiyeva.jpg",
    },
    {
        "ism": "Qudratulla Omonov",
        "muallif": "Nargiza Ismatullayeva",
        "litsenziya": "CC BY-SA 4.0",
        "havola": "https://commons.wikimedia.org/wiki/File:Qudratulla_Omonov.jpg",
    },
]

MAHALLIY_KENGASH = [
    {
        "ism": "Gulchehra Rixsiyeva",
        "harf": "GR",
        "rasm": "rixsiyeva.jpg",
        "havola": "https://uz.wikipedia.org/wiki/Gulchehra_Rixsiyeva",
        "uz": {"unvon": "Filologiya fanlari nomzodi, professor, rektor", "tashkilot": "Toshkent davlat sharqshunoslik universiteti", "mamlakat": "O'zbekiston"},
        "en": {"unvon": "PhD in Philology, Professor, Rector", "tashkilot": "Tashkent State University of Oriental Studies", "mamlakat": "Uzbekistan"},
        "tr": {"unvon": "Doktor, Prof., Rektör", "tashkilot": "Taşkent Devlet Şarkiyat Üniversitesi", "mamlakat": "Özbekistan"},
    },
    {
        "ism": "Qudratulla Omonov",
        "harf": "QO",
        "rasm": "omonov.jpg",
        "havola": "https://uz.wikipedia.org/wiki/Qudratulla_Omonov",
        "uz": {"unvon": "Filologiya fanlari doktori, professor", "tashkilot": "Toshkent davlat sharqshunoslik universiteti — turkolog", "mamlakat": "O'zbekiston"},
        "en": {"unvon": "Doctor of Philology, Professor", "tashkilot": "Tashkent State University of Oriental Studies — Turkologist", "mamlakat": "Uzbekistan"},
        "tr": {"unvon": "Doktor, Prof.", "tashkilot": "Taşkent Devlet Şarkiyat Üniversitesi — Türkolog", "mamlakat": "Özbekistan"},
    },
    {
        "ism": "Qosimjon Sodiqov",
        "harf": "QS",
        "rasm": "sodiqov.jpg",
        "havola": "https://uz.wikipedia.org/wiki/Qosimjon_Sodiqov",
        "uz": {"unvon": "Filologiya fanlari doktori, professor", "tashkilot": "Toshkent davlat sharqshunoslik universiteti — turkolog", "mamlakat": "O'zbekiston"},
        "en": {"unvon": "Doctor of Philology, Professor", "tashkilot": "Tashkent State University of Oriental Studies — Turkologist", "mamlakat": "Uzbekistan"},
        "tr": {"unvon": "Doktor, Prof.", "tashkilot": "Taşkent Devlet Şarkiyat Üniversitesi — Türkolog", "mamlakat": "Özbekistan"},
    },
    {
        "ism": "Avezov",
        "harf": "AV",
        "rasm": "avezov.jpg",
        "havola": "",
        "uz": {"unvon": "TDK rahbari", "tashkilot": "Turk Tili Qurumi (TDK)", "mamlakat": ""},
        "en": {"unvon": "Head of TDK", "tashkilot": "Turkish Language Association (TDK)", "mamlakat": ""},
        "tr": {"unvon": "TDK Başkanı", "tashkilot": "Türk Dil Kurumu (TDK)", "mamlakat": ""},
    },
    {
        "ism": "Mirzajon Kalandarov",
        "harf": "MK",
        "rasm": "kalandarov.jpg",
        "havola": "",
        "uz": {"unvon": "Dotsent, doktor", "tashkilot": "Toshkent davlat sharqshunoslik universiteti", "mamlakat": "O'zbekiston"},
        "en": {"unvon": "Assoc. Prof., PhD", "tashkilot": "Tashkent State University of Oriental Studies", "mamlakat": "Uzbekistan"},
        "tr": {"unvon": "Doç. Dr.", "tashkilot": "Taşkent Devlet Şarkiyat Üniversitesi", "mamlakat": "Özbekistan"},
    },
]


# ---------------------------------------------------------------------------
# Maqola talablari (chorlovdan)
# ---------------------------------------------------------------------------

TALABLAR = {
    "uz": [
        ("Matn bichimi", "Microsoft Word — Times New Roman, 14 pt, qatorlar oralig'i 1.5"),
        ("Ko'lami", "8–10 bet"),
        ("Sarlavha", "Birinchi qatorda o'rtada, bosh harflar bilan, quyuq rangda"),
        ("Muallif", "Keyingi qatorda o'ng tomonda: ismi-sharifi, ilmiy darajasi, "
                    "unvoni, ish joyi va e-mail manzili"),
        ("Annotatsiya", "O'zbek va ingliz tillarida 130–140 so'zli qisqacha mazmun "
                        "(Abstract) hamda tayanch tushunchalar"),
        ("Adabiyotlar", "Foydalanilgan manbalar ro'yxati maqola oxirida; matn ichida "
                        "iqtiboslar burchakli qavsda — [1, 15-b.]"),
    ],
    "en": [
        ("Text format", "Microsoft Word — Times New Roman, 14 pt, line spacing 1.5"),
        ("Length", "8–10 pages"),
        ("Title", "Centred on the first line, in uppercase and bold type"),
        ("Author", "On the following line, aligned right: full name, academic degree, "
                   "academic title, institutional affiliation and e-mail address"),
        ("Abstract", "A 130–140-word abstract and keywords in Uzbek and English"),
        ("References", "The list of references at the end of the paper; in-text "
                       "citations in square brackets — [1, p. 15]"),
    ],
    "tr": [
        ("Metin formatı", "Microsoft Word — Times New Roman, 14 pt, satır aralığı 1.5"),
        ("Sayfa sayısı", "8–10 sayfa"),
        ("Başlık", "İlk satırda ortalanmış, büyük ve koyu harflerle"),
        ("Yazar", "Bir sonraki satırda sağa dayalı: adı, soyadı, unvanı, görev yaptığı "
                  "kurum ve e-posta adresi"),
        ("Özet", "Türkçe ve İngilizce 130–140 kelimelik bildiri özeti (Abstract) ve "
                 "anahtar kelimeler"),
        ("Kaynaklar", "Kaynak listesi bildiri sonunda; metin içi atıflar köşeli "
                      "parantez içinde — [1, s. 15]"),
    ],
}

ESLATMALAR = {
    "uz": [
        "Ilmiy talablarga javob bermaydigan maqolalar qabul qilinmaydi.",
        "Anjuman materiallari alohida to'plam holida — Google Scholar va CrossRef "
        "bazalarida indekslanadigan raqamli DOI ID bilan — nashr etiladi.",
    ],
    "en": [
        "Papers that do not meet the established academic requirements will not be accepted.",
        "The conference proceedings will be published as a separate volume and assigned "
        "a digital DOI ID, with indexing in Google Scholar and Crossref.",
    ],
    "tr": [
        "Bilimsel kriterlere uymayan bildiriler kabul edilmeyecektir.",
        "Sempozyum bildirileri ayrı bir kitap hâlinde — Google Scholar ve CrossRef "
        "veritabanlarında indekslenerek dijital DOI numarası verilerek — yayımlanacaktır.",
    ],
}


# ---------------------------------------------------------------------------
# Muhim sanalar
# ---------------------------------------------------------------------------

MUHIM_SANALAR = [
    {
        "holat": "faol",
        "uz": {"sana": "2026-yil 15-noyabr", "matn": "Maqola yuborishning so'nggi kuni"},
        "en": {"sana": "November 15, 2026", "matn": "Deadline for paper submission"},
        "tr": {"sana": "15 Kasım 2026", "matn": "Bildiri gönderimi için son tarih"},
    },
    {
        "holat": "kutilmoqda",
        "uz": {"sana": "2026-yil 1-dekabr", "matn": "Qabul qilingan maqolalar e'lon qilinadi"},
        "en": {"sana": "December 1, 2026", "matn": "Announcement of accepted papers"},
        "tr": {"sana": "1 Aralık 2026", "matn": "Kabul edilen bildirilerin ilanı"},
    },
    {
        "holat": "kutilmoqda",
        "uz": {"sana": "2026-yil 15–16-dekabr", "matn": "Ilmiy yig'in kunlari"},
        "en": {"sana": "December 15–16, 2026", "matn": "Conference days"},
        "tr": {"sana": "15–16 Aralık 2026", "matn": "Sempozyum günleri"},
    },
]


# ---------------------------------------------------------------------------
# Interfeys matnlari
# ---------------------------------------------------------------------------

MATN = {
    "uz": {
        # navigatsiya
        "nav_bosh": "Bosh sahifa",
        "nav_haqida": "Yig'in haqida",
        "nav_yonalishlar": "Yo'nalishlar",
        "nav_kengash": "Ilmiy kengash",
        "nav_talablar": "Maqola talablari",
        "nav_aloqa": "Aloqa",
        "nav_yuborish": "Maqola yuborish",
        # bosh sahifa
        "chorlov": "Chorlov",
        "chorlov_murojaat": "Ardoqli bilim kishilari!",
        "chorlov_matn": "Sizni yuqoridagi mavzudagi xalqaro ilmiy yig'inga chorlaymiz.",
        "batafsil": "Batafsil",
        # qahramon va xususiyatlar
        "kashf": "Pastga",
        "xus_nishon": "Qisqacha",
        "xus_sarlavha": "Yig'in nimasi bilan ajralib turadi",
        "xus1_sarlavha": "Xalqaro ishtirok",
        "xus1_matn": "Turkiy Davlatlar Tashkiloti va Turk Tili Qurumi hamkorligida, "
                     "to'rt ish tilida o'tkaziladi.",
        "xus2_sarlavha": "Besh ilmiy yo'nalish",
        "xus2_matn": "Bitiglardan raqamli korpuslargacha — turkiy yozma merosning "
                     "barcha qatlami qamrab olinadi.",
        "xus3_sarlavha": "Toshkentda ikki kun",
        "xus3_matn": "Sharqshunoslik universitetida jonli, shu bilan birga ZOOM "
                     "orqali masofadan qatnashish imkoni bilan.",
        "xus4_sarlavha": "DOI bilan to'plam",
        "xus4_matn": "Materiallar Google Scholar va CrossRef bazalarida "
                     "indekslanadigan DOI raqami bilan nashr etiladi.",
        "qollab_nishon": "Hamkorlar",
        "qollab_sarlavha": "Tashkilotchi muassasalar",
        "hisob_kun": "kun",
        "hisob_soat": "soat",
        "hisob_daqiqa": "daqiqa",
        "hisob_soniya": "soniya",
        "yigin_boshlandi": "Ilmiy yig'in boshlandi",
        "sana_sarlavha": "Yig'in sanasi",
        "joy_sarlavha": "O'tkaziladigan joy",
        "raqam_yonalish": "ilmiy yo'nalish",
        "raqam_kun": "kun davomida",
        "raqam_til": "ish tili",
        "raqam_ekspert": "kengash a'zosi",
        "sanalar_nishon": "Muhim sanalar",
        "sanalar_sarlavha": "Muddatlarni o'tkazib yubormang",
        "yonalish_nishon": "Yo'nalishlar",
        "yonalish_sarlavha": "Ilmiy yig'in kengashlari",
        "yonalish_kirish": "Maqolangizni quyidagi besh yo'nalishdan biriga taqdim "
                           "etishingiz mumkin.",
        "kengash_nishon": "Ilmiy kengash",
        "kengash_sarlavha": "Yig'in ekspertlari",
        "kengash_kirish": "Xalqaro va mahalliy olimlardan iborat ilmiy kengash.",
        "hammasi": "Barchasini ko'rish",
        "chaqiruv_sarlavha": "Ilmiy yig'in ishtirokchisi bo'ling",
        "chaqiruv_matn": "Maqolangizni {muddat} gacha elektron pochta orqali yuboring.",
        "chaqiruv_tugma": "Maqola yuborish",
        # haqida
        "haqida_nishon": "Yig'in haqida",
        "maqsad_sarlavha": "Yig'inning bosh maqsadi",
        "tashkilotchi_sarlavha": "Tashkilotchilar",
        "malumot_sarlavha": "Umumiy ma'lumot",
        "qator_shakl": "Anjuman shakli",
        "qator_tillar": "Anjuman tillari",
        "qator_sana": "O'tkaziladigan sana",
        "qator_joy": "Manzil",
        "qator_muddat": "Maqola yuborish muddati",
        "qator_nashr": "Nashr",
        "nashr_matn": "Alohida to'plam, DOI ID bilan (Google Scholar, CrossRef)",
        # yo'nalishlar
        "yonalish_sahifa_kirish": "Yig'in beshta ilmiy kengash — yo'nalish bo'yicha "
                                  "ishlaydi. Har bir yo'nalish bo'yicha maqolalar qabul qilinadi.",
        # kengash
        "kengash_xalqaro": "Xalqaro ekspertlar",
        "kengash_mahalliy": "Bizning ekspertlar",
        "profil": "Profil",
        "rasm_manba": "Surat manbalari",
        # talablar
        "talab_nishon": "Maqola talablari",
        "talab_sarlavha": "Ilmiy maqolalarni rasmiylashtirish",
        "talab_kirish": "Maqola matni akademik andozalarda, chuqur tahliliy va ilmiy "
                        "asoslangan bo'lmog'i kerak.",
        "eslatma_sarlavha": "Eslatma",
        "qayerga_sarlavha": "Maqola qayerga yuboriladi",
        "qayerga_matn": "Tayyor maqolani quyidagi elektron pochtaga yuboring:",
        "chorlov_yuklash": "Chorlov matnini yuklab olish",
        "yoki_ajratuvchi": "yoki elektron pochta orqali yuboring",
        "maqola_forma_sarlavha": "Maqolani saytga yuklash",
        "forma_yonalish": "Ilmiy yo'nalish",
        "forma_fayl": "Maqola fayli (PDF, DOC, DOCX — 20 MB gacha)",
        "forma_maqola_yuborish": "Faylni yuborish",
        "xato_fayl": "Iltimos, ism, email va to'g'ri formatdagi faylni (PDF/DOC/DOCX, 20 MB gacha) tanlang.",
        "muvaffaqiyat_maqola": "Maqolangiz qabul qilindi. Rahmat!",
        # aloqa
        "aloqa_nishon": "Aloqa",
        "aloqa_sarlavha": "Tashkiliy qo'mita bilan bog'lanish",
        "aloqa_kirish": "Savolingiz bo'lsa quyidagi shaklni to'ldiring yoki to'g'ridan-to'g'ri "
                        "yozing — tashkiliy qo'mita javob beradi.",
        "qomita_manzili": "Tashkiliy qo'mita manzili",
        "forma_ism": "Ismingiz",
        "forma_email": "Elektron pochta",
        "forma_mavzu": "Mavzu",
        "forma_xabar": "Xabar",
        "forma_yuborish": "Yuborish",
        "forma_ixtiyoriy": "ixtiyoriy",
        # xabarlar
        "xato_forma": "Iltimos, barcha maydonlarni to'g'ri to'ldiring.",
        "muvaffaqiyat_forma": "Xabaringiz yuborildi. Rahmat!",
        "xato_404": "Kechirasiz, bunday sahifa topilmadi.",
        "xato_500": "Serverda xatolik yuz berdi. Keyinroq urinib ko'ring.",
        "bosh_sahifaga": "Bosh sahifaga qaytish",
        # futer
        "futer_bolimlar": "Bo'limlar",
        "futer_aloqa": "Aloqa",
        "futer_huquq": "Barcha huquqlar himoyalangan.",
        "admin_panel": "Admin panel",
        "yuborilmoqda": "Yuborilmoqda...",
    },
    "en": {
        "nav_bosh": "Home",
        "nav_haqida": "About",
        "nav_yonalishlar": "Sessions",
        "nav_kengash": "Committee",
        "nav_talablar": "Guidelines",
        "nav_aloqa": "Contact",
        "nav_yuborish": "Submit a paper",
        "chorlov": "Call for Papers",
        "chorlov_murojaat": "Dear scholars and distinguished academics!",
        "chorlov_matn": "You are cordially invited to participate in the international "
                        "scientific conference.",
        "batafsil": "Read more",
        # hero and highlights
        "kashf": "Scroll",
        "xus_nishon": "At a glance",
        "xus_sarlavha": "What sets this meeting apart",
        "xus1_sarlavha": "International participation",
        "xus1_matn": "Held with the Organization of Turkic States and the Turkish "
                     "Language Association, in four working languages.",
        "xus2_sarlavha": "Five thematic sessions",
        "xus2_matn": "From runic inscriptions to digital corpora — every layer of "
                     "the Turkic written heritage.",
        "xus3_sarlavha": "Two days in Tashkent",
        "xus3_matn": "On site at the University of Oriental Studies, with remote "
                     "participation over ZOOM.",
        "xus4_sarlavha": "Proceedings with DOI",
        "xus4_matn": "Papers appear in a separate volume with a DOI, indexed in "
                     "Google Scholar and CrossRef.",
        "qollab_nishon": "Partners",
        "qollab_sarlavha": "Organizing institutions",
        "hisob_kun": "days",
        "hisob_soat": "hours",
        "hisob_daqiqa": "minutes",
        "hisob_soniya": "seconds",
        "yigin_boshlandi": "The conference has begun",
        "sana_sarlavha": "Conference dates",
        "joy_sarlavha": "Venue",
        "raqam_yonalish": "thematic sessions",
        "raqam_kun": "days",
        "raqam_til": "working languages",
        "raqam_ekspert": "committee members",
        "sanalar_nishon": "Key dates",
        "sanalar_sarlavha": "Do not miss the deadlines",
        "yonalish_nishon": "Sessions",
        "yonalish_sarlavha": "Conference thematic sessions",
        "yonalish_kirish": "You may submit your paper to one of the following five sessions.",
        "kengash_nishon": "Committee",
        "kengash_sarlavha": "Conference experts",
        "kengash_kirish": "A scientific committee of international and local scholars.",
        "hammasi": "View all",
        "chaqiruv_sarlavha": "Take part in the conference",
        "chaqiruv_matn": "Send your paper by e-mail before {muddat}.",
        "chaqiruv_tugma": "Submit a paper",
        "haqida_nishon": "About",
        "maqsad_sarlavha": "Main objectives of the conference",
        "tashkilotchi_sarlavha": "Organizers",
        "malumot_sarlavha": "General information",
        "qator_shakl": "Conference format",
        "qator_tillar": "Conference languages",
        "qator_sana": "Dates",
        "qator_joy": "Address",
        "qator_muddat": "Submission deadline",
        "qator_nashr": "Publication",
        "nashr_matn": "A separate volume with a DOI ID (Google Scholar, Crossref)",
        "yonalish_sahifa_kirish": "The conference works in five thematic sessions. "
                                  "Papers are accepted in each of them.",
        "kengash_xalqaro": "International experts",
        "kengash_mahalliy": "Our experts",
        "profil": "Profile",
        "rasm_manba": "Photo credits",
        "talab_nishon": "Guidelines",
        "talab_sarlavha": "Guidelines for preparing scientific papers",
        "talab_kirish": "The paper must meet academic standards and be based on "
                        "thorough analytical and scientific research.",
        "eslatma_sarlavha": "Note",
        "qayerga_sarlavha": "Where to send the paper",
        "qayerga_matn": "Send the completed paper to the following e-mail address:",
        "chorlov_yuklash": "Download the call for papers",
        "yoki_ajratuvchi": "or send it by e-mail instead",
        "maqola_forma_sarlavha": "Upload your paper",
        "forma_yonalish": "Research track",
        "forma_fayl": "Paper file (PDF, DOC, DOCX — up to 20 MB)",
        "forma_maqola_yuborish": "Upload file",
        "xato_fayl": "Please provide your name, email and a valid file (PDF/DOC/DOCX, up to 20 MB).",
        "muvaffaqiyat_maqola": "Your paper has been received. Thank you!",
        "aloqa_nishon": "Contact",
        "aloqa_sarlavha": "Contact the organizing committee",
        "aloqa_kirish": "If you have a question, fill in the form below or write to us "
                        "directly — the organizing committee will reply.",
        "qomita_manzili": "Address of the organizing committee",
        "forma_ism": "Your name",
        "forma_email": "E-mail",
        "forma_mavzu": "Subject",
        "forma_xabar": "Message",
        "forma_yuborish": "Send",
        "forma_ixtiyoriy": "optional",
        "xato_forma": "Please fill in all fields correctly.",
        "muvaffaqiyat_forma": "Your message has been sent. Thank you!",
        "xato_404": "Sorry, this page was not found.",
        "xato_500": "A server error occurred. Please try again later.",
        "bosh_sahifaga": "Back to home",
        "futer_bolimlar": "Sections",
        "futer_aloqa": "Contact",
        "futer_huquq": "All rights reserved.",
        "admin_panel": "Admin panel",
        "yuborilmoqda": "Sending...",
    },
    "tr": {
        "nav_bosh": "Ana sayfa",
        "nav_haqida": "Sempozyum",
        "nav_yonalishlar": "Konu başlıkları",
        "nav_kengash": "Kurullar",
        "nav_talablar": "Bildiri çağrısı",
        "nav_aloqa": "İletişim",
        "nav_yuborish": "Bildiri gönder",
        "chorlov": "Sempozyum çağrısı",
        "chorlov_murojaat": "Değerli bilim insanları ve araştırmacılar!",
        "chorlov_matn": "Sizleri uluslararası sempozyuma davet etmekten mutluluk duyuyoruz.",
        "batafsil": "Ayrıntılar",
        # kahraman ve öne çıkanlar
        "kashf": "Aşağı",
        "xus_nishon": "Kısaca",
        "xus_sarlavha": "Sempozyumu ayıran nitelikler",
        "xus1_sarlavha": "Uluslararası katılım",
        "xus1_matn": "Türk Devletleri Teşkilatı ve Türk Dil Kurumu iş birliğiyle, "
                     "dört çalışma dilinde düzenlenir.",
        "xus2_sarlavha": "Beş çalışma başlığı",
        "xus2_matn": "Runik yazıtlardan dijital derlemlere — Türk yazılı mirasının "
                     "bütün katmanları.",
        "xus3_sarlavha": "Taşkent'te iki gün",
        "xus3_matn": "Şarkiyat Üniversitesi'nde yüz yüze, ayrıca ZOOM üzerinden "
                     "uzaktan katılım imkânıyla.",
        "xus4_sarlavha": "DOI'li bildiri kitabı",
        "xus4_matn": "Bildiriler Google Scholar ve CrossRef'te dizinlenen DOI "
                     "numarasıyla ayrı bir kitapta yayımlanır.",
        "qollab_nishon": "Paydaşlar",
        "qollab_sarlavha": "Düzenleyen kurumlar",
        "hisob_kun": "gün",
        "hisob_soat": "saat",
        "hisob_daqiqa": "dakika",
        "hisob_soniya": "saniye",
        "yigin_boshlandi": "Sempozyum başladı",
        "sana_sarlavha": "Sempozyum tarihi",
        "joy_sarlavha": "Yer",
        "raqam_yonalish": "çalışma başlığı",
        "raqam_kun": "gün boyunca",
        "raqam_til": "kongre dili",
        "raqam_ekspert": "kurul üyesi",
        "sanalar_nishon": "Önemli tarihler",
        "sanalar_sarlavha": "Son tarihleri kaçırmayın",
        "yonalish_nishon": "Konu başlıkları",
        "yonalish_sarlavha": "Sempozyum çalışma başlıkları",
        "yonalish_kirish": "Bildirinizi aşağıdaki beş başlıktan birine sunabilirsiniz.",
        "kengash_nishon": "Kurullar",
        "kengash_sarlavha": "Sempozyum uzmanları",
        "kengash_kirish": "Uluslararası ve yerli bilim insanlarından oluşan bilim kurulu.",
        "hammasi": "Tümünü gör",
        "chaqiruv_sarlavha": "Sempozyuma katılın",
        "chaqiruv_matn": "Bildirinizi {muddat} tarihine kadar e-posta ile gönderin.",
        "chaqiruv_tugma": "Bildiri gönder",
        "haqida_nishon": "Sempozyum",
        "maqsad_sarlavha": "Bilimsel toplantının temel amacı",
        "tashkilotchi_sarlavha": "Düzenleyen kurumlar",
        "malumot_sarlavha": "Genel bilgiler",
        "qator_shakl": "Sempozyum biçimi",
        "qator_tillar": "Kongre dilleri",
        "qator_sana": "Tarih",
        "qator_joy": "Adres",
        "qator_muddat": "Bildiri gönderim son tarihi",
        "qator_nashr": "Yayın",
        "nashr_matn": "Ayrı bir kitap, DOI numarası ile (Google Scholar, CrossRef)",
        "yonalish_sahifa_kirish": "Sempozyum beş çalışma başlığı altında yürütülür. "
                                  "Her başlık için bildiri kabul edilmektedir.",
        "kengash_xalqaro": "Uluslararası uzmanlar",
        "kengash_mahalliy": "Bizim uzmanlarımız",
        "profil": "Profil",
        "rasm_manba": "Fotoğraf kaynakları",
        "talab_nishon": "Bildiri çağrısı",
        "talab_sarlavha": "Gönderilecek bildirilerin biçimsel özellikleri",
        "talab_kirish": "Bildiri metni akademik standartlara uygun, derinlemesine analiz "
                        "içeren ve bilimsel temellere dayanan bir yapıda olmalıdır.",
        "eslatma_sarlavha": "Not",
        "qayerga_sarlavha": "Bildiri nereye gönderilir",
        "qayerga_matn": "Hazır bildiriyi aşağıdaki e-posta adresine gönderin:",
        "chorlov_yuklash": "Sempozyum çağrısını indir",
        "yoki_ajratuvchi": "veya e-posta ile gönderin",
        "maqola_forma_sarlavha": "Bildirinizi yükleyin",
        "forma_yonalish": "Bilimsel alan",
        "forma_fayl": "Bildiri dosyası (PDF, DOC, DOCX — 20 MB'a kadar)",
        "forma_maqola_yuborish": "Dosyayı gönder",
        "xato_fayl": "Lütfen adınızı, e-postanızı ve geçerli bir dosya (PDF/DOC/DOCX, 20 MB'a kadar) seçin.",
        "muvaffaqiyat_maqola": "Bildiriniz alındı. Teşekkür ederiz!",
        "aloqa_nishon": "İletişim",
        "aloqa_sarlavha": "Düzenleme kurulu ile iletişim",
        "aloqa_kirish": "Sorunuz varsa aşağıdaki formu doldurun veya doğrudan yazın — "
                        "düzenleme kurulu yanıtlayacaktır.",
        "qomita_manzili": "Düzenleme kurulu adresi",
        "forma_ism": "Adınız",
        "forma_email": "E-posta",
        "forma_mavzu": "Konu",
        "forma_xabar": "Mesaj",
        "forma_yuborish": "Gönder",
        "forma_ixtiyoriy": "isteğe bağlı",
        "xato_forma": "Lütfen tüm alanları doğru doldurun.",
        "muvaffaqiyat_forma": "Mesajınız gönderildi. Teşekkürler!",
        "xato_404": "Üzgünüz, bu sayfa bulunamadı.",
        "xato_500": "Sunucuda bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
        "bosh_sahifaga": "Ana sayfaya dön",
        "futer_bolimlar": "Bölümler",
        "futer_aloqa": "İletişim",
        "futer_huquq": "Tüm hakları saklıdır.",
        "admin_panel": "Admin panel",
        "yuborilmoqda": "Gönderiliyor...",
    },
}


# Chorlov PDF fayllari — static/chorlov/ ichiga qo'yiladi
CHORLOV_FAYL = {
    "uz": "chorlov-uz.pdf",
    "en": "call-for-papers-en.pdf",
    "tr": "sempozyum-cagrisi-tr.pdf",
}


# ---------------------------------------------------------------------------
# Yordamchi: ko'p tilli yozuvdan bitta tilni ajratib oladi
# ---------------------------------------------------------------------------

def mahalliy(element, til):
    """Umumiy maydonlar + tanlangan tildagi maydonlarni bitta lug'atga qo'shadi.

    {"id": 1, "uz": {"nom": "..."}, "en": {...}} -> {"id": 1, "nom": "..."}
    """
    natija = {k: v for k, v in element.items() if k not in TILLAR}
    natija.update(element.get(til) or element[ASOSIY_TIL])
    return natija


def royxat(elementlar, til):
    """Ro'yxatdagi har bir elementni `mahalliy()` orqali o'tkazadi."""
    return [mahalliy(e, til) for e in elementlar]
