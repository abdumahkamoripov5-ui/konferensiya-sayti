# -*- coding: utf-8 -*-
"""Ma'lumotlar bazasi bilan ishlash (sqlite3, tashqi kutubxonasiz).

Saytda maqola yuborish formasi yo'q — maqolalar elektron pochta orqali
qabul qilinadi. Shuning uchun bazada faqat aloqa xabarlari saqlanadi.
"""

import os
import sqlite3
from datetime import datetime

from flask import current_app, g

SXEMA = """
CREATE TABLE IF NOT EXISTS xabarlar (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ism         TEXT NOT NULL,
    email       TEXT NOT NULL,
    mavzu       TEXT,
    xabar       TEXT NOT NULL,
    til         TEXT NOT NULL DEFAULT 'uz',
    oqilgan     INTEGER NOT NULL DEFAULT 0,
    yaratilgan  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_xabar_oqilgan ON xabarlar(oqilgan);

CREATE TABLE IF NOT EXISTS maqolalar (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ism           TEXT NOT NULL,
    email         TEXT NOT NULL,
    yonalish      TEXT,
    fayl_nomi     TEXT NOT NULL,
    original_nomi TEXT NOT NULL,
    til           TEXT NOT NULL DEFAULT 'uz',
    yaratilgan    TEXT NOT NULL
);
"""


def get_db():
    """So'rov davomida yagona ulanishni qaytaradi."""
    if "db" not in g:
        yol = current_app.config["DATABASE"]
        os.makedirs(os.path.dirname(yol), exist_ok=True)
        g.db = sqlite3.connect(yol, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Jadvallarni yaratadi va close_db'ni ilovaga ulaydi."""
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = get_db()
        db.executescript(SXEMA)
        # Eskirgan sxemadan qolgan bazalarda `til` ustuni bo'lmasligi mumkin
        ustunlar = {q["name"] for q in db.execute("PRAGMA table_info(xabarlar)")}
        if "til" not in ustunlar:
            db.execute("ALTER TABLE xabarlar ADD COLUMN til TEXT NOT NULL DEFAULT 'uz'")
        db.commit()


# --- Xabarlar --------------------------------------------------------------

def xabar_qoshish(ism, email, mavzu, xabar, til="uz"):
    db = get_db()
    db.execute(
        """INSERT INTO xabarlar (ism, email, mavzu, xabar, til, yaratilgan)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (ism, email, mavzu, xabar, til, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    db.commit()


def xabarlar_royxati(faqat_oqilmagan=False):
    db = get_db()
    if faqat_oqilmagan:
        return db.execute(
            "SELECT * FROM xabarlar WHERE oqilgan = 0 ORDER BY id DESC"
        ).fetchall()
    return db.execute("SELECT * FROM xabarlar ORDER BY id DESC").fetchall()


def xabar_oqildi(xabar_id):
    db = get_db()
    db.execute("UPDATE xabarlar SET oqilgan = 1 WHERE id = ?", (xabar_id,))
    db.commit()


def xabar_ochirish(xabar_id):
    db = get_db()
    db.execute("DELETE FROM xabarlar WHERE id = ?", (xabar_id,))
    db.commit()


# --- Statistika ------------------------------------------------------------

def statistika():
    db = get_db()
    jami = db.execute("SELECT COUNT(*) AS n FROM xabarlar").fetchone()["n"]
    oqilmagan = db.execute(
        "SELECT COUNT(*) AS n FROM xabarlar WHERE oqilgan = 0"
    ).fetchone()["n"]
    return {"jami": jami, "oqilmagan": oqilmagan}


# --- Maqolalar ---------------------------------------------------------------

def maqola_qoshish(ism, email, yonalish, fayl_nomi, original_nomi, til="uz"):
    db = get_db()
    db.execute(
        """INSERT INTO maqolalar (ism, email, yonalish, fayl_nomi, original_nomi, til, yaratilgan)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (ism, email, yonalish, fayl_nomi, original_nomi, til,
         datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    db.commit()


def maqolalar_royxati():
    db = get_db()
    return db.execute("SELECT * FROM maqolalar ORDER BY id DESC").fetchall()


def maqola_topish(maqola_id):
    db = get_db()
    return db.execute("SELECT * FROM maqolalar WHERE id = ?", (maqola_id,)).fetchone()


def maqola_ochirish(maqola_id):
    db = get_db()
    db.execute("DELETE FROM maqolalar WHERE id = ?", (maqola_id,))
    db.commit()
