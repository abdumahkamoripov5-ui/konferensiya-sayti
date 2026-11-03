# -*- coding: utf-8 -*-
"""Ma'lumotlar bazasi: lokal SQLite yoki DATABASE_URL orqali PostgreSQL.

Ikkita jadval: aloqa xabarlari va saytga yuklangan maqolalar (admin
tasdiqlagandan keyingina jamoatchilikka ochiq bo'ladi).
"""

import os
import sqlite3
from datetime import datetime
import time
import hashlib
import math

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

CREATE TABLE IF NOT EXISTS request_limits (
    bucket TEXT PRIMARY KEY,
    hits INTEGER NOT NULL,
    expires BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS qatnashchilar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ism TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    tashkilot TEXT NOT NULL,
    format TEXT NOT NULL,
    til TEXT NOT NULL,
    yaratilgan TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS maqolalar (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ism           TEXT NOT NULL,
    email         TEXT NOT NULL,
    sarlavha      TEXT,
    yonalish      TEXT,
    fayl_nomi     TEXT NOT NULL,
    original_nomi TEXT NOT NULL,
    til           TEXT NOT NULL DEFAULT 'uz',
    holat         TEXT NOT NULL DEFAULT 'kutilmoqda',
    yaratilgan    TEXT NOT NULL
);
"""


def get_db():
    """So'rov davomida yagona ulanishni qaytaradi."""
    if "db" not in g:
        if current_app.config.get("DATABASE_URL"):
            import psycopg
            from psycopg.rows import dict_row
            g.db = psycopg.connect(
                current_app.config["DATABASE_URL"], row_factory=dict_row,
                prepare_threshold=None, sslmode="require", connect_timeout=10,
            )
            return g.db
        if os.environ.get("VERCEL"):
            raise RuntimeError("Vercelda DATABASE_URL muhit o'zgaruvchisini sozlang.")
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
        if app.config.get("DATABASE_URL"):
            sxema = SXEMA.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY")
            for statement in sxema.split(";"):
                if statement.strip():
                    db.execute(statement)
            db.execute("ALTER TABLE maqolalar ADD COLUMN IF NOT EXISTS fayl_data BYTEA")
            # Supabase Data API orqali anonim kirishni yopish.
            for name, kind in (("tracking_token", "TEXT"), ("file_hash", "TEXT"), ("izoh", "TEXT NOT NULL DEFAULT ''")):
                db.execute(f"ALTER TABLE maqolalar ADD COLUMN IF NOT EXISTS {name} {kind}")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tracking_token ON maqolalar(tracking_token)")
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_paper_duplicate ON maqolalar(email, file_hash)")
            for jadval in ("xabarlar", "maqolalar", "request_limits", "qatnashchilar"):
                db.execute(f"ALTER TABLE {jadval} ENABLE ROW LEVEL SECURITY")
            db.commit()
            return
        db.executescript(SXEMA)
        # Eskirgan sxemadan qolgan bazalarda `til` ustuni bo'lmasligi mumkin
        ustunlar = {q["name"] for q in db.execute("PRAGMA table_info(xabarlar)")}
        if "til" not in ustunlar:
            db.execute("ALTER TABLE xabarlar ADD COLUMN til TEXT NOT NULL DEFAULT 'uz'")
        maqola_ustunlar = {q["name"] for q in db.execute("PRAGMA table_info(maqolalar)")}
        if "sarlavha" not in maqola_ustunlar:
            db.execute("ALTER TABLE maqolalar ADD COLUMN sarlavha TEXT")
        if "holat" not in maqola_ustunlar:
            db.execute("ALTER TABLE maqolalar ADD COLUMN holat TEXT NOT NULL DEFAULT 'kutilmoqda'")
        for name, kind in (("tracking_token", "TEXT"), ("file_hash", "TEXT"), ("izoh", "TEXT NOT NULL DEFAULT ''")):
            if name not in maqola_ustunlar:
                db.execute(f"ALTER TABLE maqolalar ADD COLUMN {name} {kind}")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tracking_token ON maqolalar(tracking_token)")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_paper_duplicate ON maqolalar(email, file_hash)")
        db.commit()


def execute(db, query, params=()):
    """SQLite parametrlarini PostgreSQL uchun moslash."""
    if current_app.config.get("DATABASE_URL"):
        query = query.replace("?", "%s")
    return db.execute(query, params)


# --- Xabarlar --------------------------------------------------------------

def xabar_qoshish(ism, email, mavzu, xabar, til="uz"):
    db = get_db()
    execute(db,
        """INSERT INTO xabarlar (ism, email, mavzu, xabar, til, yaratilgan)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (ism, email, mavzu, xabar, til, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    db.commit()


def xabarlar_royxati(faqat_oqilmagan=False):
    db = get_db()
    if faqat_oqilmagan:
        return execute(db,
            "SELECT * FROM xabarlar WHERE oqilgan = 0 ORDER BY id DESC"
        ).fetchall()
    return execute(db, "SELECT * FROM xabarlar ORDER BY id DESC").fetchall()


def xabar_oqildi(xabar_id):
    db = get_db()
    execute(db, "UPDATE xabarlar SET oqilgan = 1 WHERE id = ?", (xabar_id,))
    db.commit()


def xabar_ochirish(xabar_id):
    db = get_db()
    execute(db, "DELETE FROM xabarlar WHERE id = ?", (xabar_id,))
    db.commit()


# --- Statistika ------------------------------------------------------------

def statistika():
    db = get_db()
    jami = execute(db, "SELECT COUNT(*) AS n FROM xabarlar").fetchone()["n"]
    oqilmagan = execute(db,
        "SELECT COUNT(*) AS n FROM xabarlar WHERE oqilgan = 0"
    ).fetchone()["n"]
    return {"jami": jami, "oqilmagan": oqilmagan}


# --- Maqolalar ---------------------------------------------------------------

def maqola_qoshish(ism, email, sarlavha, yonalish, fayl_nomi, original_nomi, til="uz", fayl_data=None, tracking_token=None, file_hash=None):
    db = get_db()
    columns = "ism, email, sarlavha, yonalish, fayl_nomi, original_nomi, til, yaratilgan, tracking_token, file_hash"
    params = [ism, email, sarlavha, yonalish, fayl_nomi, original_nomi, til,
              datetime.now().strftime("%Y-%m-%d %H:%M"), tracking_token, file_hash]
    if current_app.config.get("DATABASE_URL"):
        columns += ", fayl_data"
        params.append(fayl_data)
    placeholders = ", ".join("?" for _ in params)
    row = execute(db, f"INSERT INTO maqolalar ({columns}) VALUES ({placeholders}) "
                  "ON CONFLICT (email, file_hash) DO NOTHING RETURNING id", params).fetchone()
    db.commit()
    return row["id"] if row else None


def maqolalar_royxati():
    db = get_db()
    return execute(db, "SELECT id, ism, email, sarlavha, yonalish, fayl_nomi, original_nomi, til, holat, yaratilgan, tracking_token, izoh FROM maqolalar ORDER BY id DESC").fetchall()


def maqolalar_tasdiqlangan():
    db = get_db()
    return execute(db,
        "SELECT id, ism, email, sarlavha, yonalish, fayl_nomi, original_nomi, til, holat, yaratilgan, tracking_token, izoh FROM maqolalar WHERE holat = 'tasdiqlangan' ORDER BY id DESC"
    ).fetchall()


def maqola_topish(maqola_id):
    db = get_db()
    return execute(db, "SELECT id, ism, email, sarlavha, yonalish, fayl_nomi, original_nomi, til, holat, yaratilgan, tracking_token, izoh FROM maqolalar WHERE id = ?", (maqola_id,)).fetchone()


def maqola_tasdiqlash(maqola_id):
    db = get_db()
    execute(db, "UPDATE maqolalar SET holat = 'tasdiqlangan' WHERE id = ?", (maqola_id,))
    db.commit()


def maqola_ochirish(maqola_id):
    db = get_db()
    execute(db, "DELETE FROM maqolalar WHERE id = ?", (maqola_id,))
    db.commit()


def maqola_fayli(maqola_id):
    db = get_db()
    row = execute(db, "SELECT fayl_data FROM maqolalar WHERE id = ?", (maqola_id,)).fetchone()
    return bytes(row["fayl_data"]) if row and row["fayl_data"] is not None else None


HOLATLAR = ("kutilmoqda", "korib_chiqilmoqda", "tuzatish_kerak", "tasdiqlangan", "rad_etilgan")


def maqola_holatini_ozgartirish(maqola_id, holat, izoh):
    if holat not in HOLATLAR:
        raise ValueError("Unknown status")
    db = get_db()
    execute(db, "UPDATE maqolalar SET holat = ?, izoh = ? WHERE id = ?", (holat, izoh, maqola_id))
    db.commit()


def maqola_token_bilan(token):
    return execute(get_db(), "SELECT id, sarlavha, holat, izoh, yaratilgan FROM maqolalar WHERE tracking_token = ?", (token,)).fetchone()


def rate_limit(scope, identity, limit, seconds):
    """Database-backed fixed windows shared by workers and serverless instances."""
    now = int(time.time())
    window = now // seconds
    bucket = hashlib.sha256(f"{scope}:{identity}:{window}".encode()).hexdigest()
    expires = (window + 1) * seconds
    db = get_db()
    execute(db, "DELETE FROM request_limits WHERE expires <= ?", (now,))
    row = execute(db, """INSERT INTO request_limits (bucket, hits, expires) VALUES (?, 1, ?)
        ON CONFLICT (bucket) DO UPDATE SET hits = request_limits.hits + 1
        RETURNING hits""", (bucket, expires)).fetchone()
    db.commit()
    return row["hits"] <= limit, max(1, expires - now)


def paginated(kind, page=1, search="", status="", unread=False):
    table = {"messages": "xabarlar", "papers": "maqolalar", "participants": "qatnashchilar"}[kind]
    clauses, params = [], []
    if search:
        fields = {"xabarlar": ("ism", "email", "mavzu", "xabar"),
                  "maqolalar": ("ism", "email", "sarlavha", "yonalish"),
                  "qatnashchilar": ("ism", "email", "tashkilot")}[table]
        clauses.append("(" + " OR ".join(f"LOWER({f}) LIKE LOWER(?)" for f in fields) + ")")
        params.extend([f"%{search}%"] * len(fields))
    if unread and table == "xabarlar":
        clauses.append("oqilgan = 0")
    if status and table == "maqolalar":
        clauses.append("holat = ?")
        params.append(status)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    db = get_db()
    total = execute(db, f"SELECT COUNT(*) AS n FROM {table}{where}", params).fetchone()["n"]
    pages = max(1, math.ceil(total / 20))
    page = min(max(1, page), pages)
    # Never read file blobs for a listing.
    columns = "id, ism, email, sarlavha, yonalish, original_nomi, til, holat, izoh, yaratilgan" if table == "maqolalar" else "*"
    rows = execute(db, f"SELECT {columns} FROM {table}{where} ORDER BY id DESC LIMIT ? OFFSET ?", params + [20, (page - 1) * 20]).fetchall()
    return {"rows": rows, "total": total, "page": page, "pages": pages}


def qatnashchi_qoshish(ism, email, tashkilot, format, til):
    db = get_db()
    row = execute(db, """INSERT INTO qatnashchilar (ism, email, tashkilot, format, til, yaratilgan)
        VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (email) DO NOTHING RETURNING id""",
        (ism, email, tashkilot, format, til, datetime.now().strftime("%Y-%m-%d %H:%M"))).fetchone()
    db.commit()
    return row["id"] if row else None
