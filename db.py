import sqlite3
from datetime import datetime

DB_NAME = "currency.db"


def init_db() -> None:
    """Инициализация БД и создание таблицы курсов."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_currency TEXT NOT NULL UNIQUE,
                rate REAL NOT NULL,
                updated_at TEXT NOT NULL
            )
            """)


def save_rate(id: int, target_currency: str, rate: float) -> None:
    """Сохранение или обновление курса валюты."""
    target_currency = target_currency.upper()
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            "SELECT id FROM rates WHERE target_currency = ?",
            (target_currency,),
        )
        row = cur.fetchone()

        if row:
            conn.execute(
                """
                UPDATE rates
                SET rate = ?, updated_at = ?
                WHERE target_currency = ?
                """,
                (rate, updated_at, target_currency),
            )
        else:
            try:
                conn.execute(
                    """
                    INSERT INTO rates (id, target_currency, rate, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (id, target_currency, rate, updated_at),
                )
            except sqlite3.IntegrityError:
                # Если id уже занят другой валютой, вставляем без явного id
                conn.execute(
                    """
                    INSERT INTO rates (target_currency, rate, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    (target_currency, rate, updated_at),
                )


def get_saved_rate(target_currency: str):
    """Получение сохранённого курса валюты."""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            "SELECT rate FROM rates WHERE target_currency = ?",
            (target_currency.upper(),),
        )
        row = cur.fetchone()

    return row[0] if row else None
