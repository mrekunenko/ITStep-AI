import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# 1) Завантажуємо .env саме з папки проєкту
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2) Діагностика змінних (корисно)
print("DB_HOST =", os.getenv("DB_HOST"))
print("DB_PORT =", os.getenv("DB_PORT"))
print("DB_NAME =", os.getenv("DB_NAME"))
print("DB_USER =", os.getenv("DB_USER"))
print("DB_SSLMODE =", os.getenv("DB_SSLMODE"))
print("DB_PASSWORD set =", bool(os.getenv("DB_PASSWORD")))

# 3) Підключення
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 5432)),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode=os.getenv("DB_SSLMODE"),
)

with conn.cursor() as cur:
    # 4) Версія Postgres (перевірка конекту)
    cur.execute("SELECT version();")
    print("Postgres version:", cur.fetchone()[0])
    cur.execute("""
        SELECT d.name, COUNT(doc.id)
        FROM public.departments d
        LEFT JOIN public.doctors doc ON doc.department_id = d.id
        GROUP BY d.name
        ORDER BY 2 DESC;
    """)
    print("doctors per department:", cur.fetchall()[:5])
    # 5) Які є таблиці в public
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public' AND table_type='BASE TABLE'
        ORDER BY 1;
    """)
    public_tables = [r[0] for r in cur.fetchall()]
    print("public tables:", public_tables)

    # 6) (опціонально) показати всі таблиці по всіх схемах
    cur.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
        ORDER BY table_schema, table_name;
    """)
    rows = cur.fetchall()
    print("Tables found:", len(rows))

conn.close()

