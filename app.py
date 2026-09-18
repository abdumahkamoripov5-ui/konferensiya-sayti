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
from functools import wraps

from flask import (Flask, flash, g, redirect, render_template, request,
                   Response, send_from_directory, session, url_for)
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

import config
import models

app = Flask(__name__)
app.config.from_object(config.Config)

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
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$", email or ""))


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
        if not form["ism"] or not email_togrimi(form["email"]) or len(form["xabar"]) < 10:
            flash(config.MATN[til]["xato_forma"], "xato")
            return render_template("aloqa.html", faol="aloqa", form=form)

        models.xabar_qoshish(form["ism"], form["email"], form["mavzu"],
                             form["xabar"], til)
        flash(config.MATN[til]["muvaffaqiyat_forma"], "muvaffaqiyat")
        return redirect(url_for("aloqa"))

    return render_template("aloqa.html", faol="aloqa", form={})


def fayl_togrimi(fayl):
    if not fayl or not fayl.filename:
        return False
    kengaytma = fayl.filename.rsplit(".", 1)[-1].lower() if "." in fayl.filename else ""
    return kengaytma in config.Config.MAQOLA_KENGAYTMALAR


@app.route("/maqola-yuborish", defaults={"til": config.ASOSIY_TIL}, methods=["GET", "POST"])
@app.route(f"/<any({QOSHIMCHA_TILLAR}):til>/maqola-yuborish", methods=["GET", "POST"])
def maqola_yuborish():
    til = g.til
    if request.method == "POST":
        form = {
            "ism": (request.form.get("ism") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "yonalish": (request.form.get("yonalish") or "").strip(),
        }
        fayl = request.files.get("fayl")

        if not form["ism"] or not email_togrimi(form["email"]) or not fayl_togrimi(fayl):
            flash(config.MATN[til]["xato_fayl"], "xato")
            return redirect(url_for("talablar", til=til) + "#yuborish")

        os.makedirs(app.config["MAQOLA_PAPKA"], exist_ok=True)
        kengaytma = fayl.filename.rsplit(".", 1)[-1].lower()
        fayl_nomi = f"{uuid.uuid4().hex}.{kengaytma}"
        fayl.save(os.path.join(app.config["MAQOLA_PAPKA"], fayl_nomi))

        models.maqola_qoshish(form["ism"], form["email"], form["yonalish"],
                              fayl_nomi, secure_filename(fayl.filename), til)
        flash(config.MATN[til]["muvaffaqiyat_maqola"], "muvaffaqiyat")
        return redirect(url_for("talablar", til=til) + "#yuborish")

    return redirect(url_for("talablar", til=til) + "#yuborish")


@app.errorhandler(RequestEntityTooLarge)
def fayl_katta(e):
    til = g.get("til", config.ASOSIY_TIL)
    flash(config.MATN[til]["xato_fayl"], "xato")
    return redirect(url_for("talablar", til=til) + "#yuborish")


# --- Admin panel -----------------------------------------------------------

@app.route("/admin/kirish", methods=["GET", "POST"])
def admin_kirish():
    if request.method == "POST":
        login = request.form.get("login", "")
        parol = request.form.get("parol", "")
        if login == app.config["ADMIN_LOGIN"] and parol == app.config["ADMIN_PAROL"]:
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        flash("Login yoki parol noto'g'ri.", "xato")
    return render_template("admin_kirish.html")


@app.route("/admin/chiqish")
def admin_chiqish():
    session.pop("admin", None)
    return redirect(url_for("bosh_sahifa"))


@app.route("/admin")
@admin_kerak
def admin_panel():
    faqat_yangi = request.args.get("holat") == "yangi"
    return render_template(
        "admin.html",
        xabarlar=models.xabarlar_royxati(faqat_yangi),
        stat=models.statistika(),
        faqat_yangi=faqat_yangi,
        maqolalar=models.maqolalar_royxati(),
    )


@app.route("/admin/maqola/<int:maqola_id>/yuklab-olish")
@admin_kerak
def admin_maqola_yuklab_olish(maqola_id):
    maqola = models.maqola_topish(maqola_id)
    if maqola is None:
        return redirect(url_for("admin_panel"))
    return send_from_directory(
        app.config["MAQOLA_PAPKA"], maqola["fayl_nomi"],
        as_attachment=True, download_name=maqola["original_nomi"],
    )


@app.route("/admin/maqola/<int:maqola_id>/ochirish", methods=["POST"])
@admin_kerak
def admin_maqola_ochirish(maqola_id):
    maqola = models.maqola_topish(maqola_id)
    if maqola is not None:
        fayl_yoli = os.path.join(app.config["MAQOLA_PAPKA"], maqola["fayl_nomi"])
        if os.path.exists(fayl_yoli):
            os.remove(fayl_yoli)
        models.maqola_ochirish(maqola_id)
        flash("Maqola o'chirildi.", "muvaffaqiyat")
    return redirect(url_for("admin_panel"))


@app.route("/admin/oqildi/<int:xabar_id>", methods=["POST"])
@admin_kerak
def admin_oqildi(xabar_id):
    models.xabar_oqildi(xabar_id)
    return redirect(request.referrer or url_for("admin_panel"))


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
        yozuvchi.writerow([q["id"], q["ism"], q["email"], q["mavzu"],
                           q["xabar"], q["til"], q["yaratilgan"]])

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


models.init_db(app)

if __name__ == "__main__":
    # Tuzatish rejimi (debug) faqat shu mashinada ishlaganda yoqiladi.
    # U yoqilganda xatolik sahifasida interaktiv konsol ochiladi — o'sha
    # konsol orqali serverda buyruq bajarsa bo'ladi. Shuning uchun sayt
    # tashqariga chiqarilganda DEBUG hech qachon yoqilmasligi kerak.
    debug = os.environ.get("DEBUG", "1") == "1"
    app.run(debug=debug, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
