# sql_tools.py
import os
import dotenv
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase

# Завантажити .env файл
dotenv.load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543")
DB_NAME = os.getenv("DB_NAME", "postgres")

if not DB_USER:
    raise ValueError("DB_USER не знайдено у .env")
if not DB_PASSWORD:
    raise ValueError("SUPABASE_DB_PASSWORD не знайдено у .env")
if not DB_HOST:
    raise ValueError("DB_HOST не знайдено у .env")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
)

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    future=True,
)

try:
    import streamlit as st


    @st.cache_resource
    def get_sql_db():
        return SQLDatabase(engine)


    db = get_sql_db()
except Exception:
    db = SQLDatabase(engine)


@tool
def show_db_schema() -> str:
    """Показати схему бази даних (таблиці та колонки)."""
    q = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name IN (
        'doctors','departments','wards','vacations',
        'specializations','doctors_specializations',
        'examinations','doctors_examinations',
        'diseases','donations','sponsors'
    )
    ORDER BY table_name, ordinal_position;
    """
    try:
        return db.run(q)
    except Exception as e:
        return f"Помилка schema lookup: {str(e)}"


@tool
def run_sql_query(query: str) -> str:
    """
    Виконати SELECT запит до бази даних лікарні.
    Повертає результати у вигляді таблиці або списку.
    Використовується для перегляду даних про лікарів, відділення, обстеження, донації, відпустки.
    """
    query = (query or "").strip()

    if not query:
        return "Порожній запит."

    if not query.upper().startswith("SELECT"):
        return "Дозволені лише SELECT запити."

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())

        if not rows:
            return "Запит виконано, але результатів не знайдено."

        # ✅ Приховуємо ID колонки (включаючи doctor_id, department_id тощо)
        safe_columns = []
        safe_indices = []

        for i, col in enumerate(columns):
            col_lower = col.lower()
            # Приховуємо будь-які ID колонки
            if col_lower == 'id' or col_lower.endswith('_id'):
                continue
            safe_columns.append(col)
            safe_indices.append(i)

        if not safe_columns:
            return "Всі колонки приховані (тільки ID)"

        # ✅ ЯКЩО 1 КОЛОНКА → НУМЕРОВАНИЙ СПИСОК (БЕЗ НАЗВИ КОЛОНКИ)
        if len(safe_columns) == 1:
            items = []
            for i, row in enumerate(rows, 1):
                value = row[safe_indices[0]]
                display_value = "-" if value is None else str(value)
                items.append(f"{i}. {display_value}")

            result_text = "\n".join(items)
            return f"Знайдено записів: {len(rows)}\n\n{result_text}"

        # ✅ 2+ КОЛОНКИ → MARKDOWN ТАБЛИЦЯ
        header = " | ".join(safe_columns)
        separator = " | ".join(["---"] * len(safe_columns))

        data_rows = []
        for row in rows:
            safe_values = [row[i] for i in safe_indices]
            formatted = [
                "-" if v is None else str(v)[:50]
                for v in safe_values
            ]
            data_rows.append(" | ".join(formatted))

        table = f"{header}\n{separator}\n" + "\n".join(data_rows)
        return f"Знайдено записів: {len(rows)}\n\n{table}"

    except Exception as e:
        return f"Помилка виконання запиту: {str(e)}"


@tool
def get_doctor_id(name: str = "", surname: str = "") -> str:
    """
    Знайти ID лікаря за ім'ям та/або прізвищем.
    Можна передати тільки прізвище (name="") або тільки ім'я (surname="").

    :param name: Ім'я лікаря (опціонально)
    :param surname: Прізвище лікаря (опціонально)
    :return: ID лікаря або повідомлення про помилку
    """
    try:
        name = (name or "").strip()
        surname = (surname or "").strip()

        if not name and not surname:
            return "Необхідно вказати хоча б ім'я або прізвище"

        # Формуємо запит динамічно
        conditions = []
        params = {}

        if surname:
            conditions.append("LOWER(surname) = LOWER(:surname)")
            params["surname"] = surname

        if name:
            conditions.append("LOWER(name) = LOWER(:name)")
            params["name"] = name

        where_clause = " AND ".join(conditions)

        query = text(f"""
            SELECT id, surname, name, patronymic 
            FROM doctors 
            WHERE {where_clause}
        """)

        with engine.connect() as conn:
            result = conn.execute(query, params)
            rows = result.fetchall()

        if not rows:
            search_term = f"'{name} {surname}'" if name and surname else f"'{surname or name}'"
            return f"Лікаря {search_term} не знайдено в базі даних"

        if len(rows) > 1:
            options = "\n".join([
                f"ID={row[0]}: {row[1]} {row[2]} {row[3] or ''}"
                for row in rows
            ])
            return f"Знайдено {len(rows)} лікарів:\n{options}\n\nУточніть запит"

        doctor = rows[0]
        full_name = f"{doctor[1]} {doctor[2]} {doctor[3] or ''}".strip()
        return f"ID лікаря {full_name}: {doctor[0]}"

    except Exception as e:
        return f"Помилка пошуку: {str(e)}"


@tool
def add_vacation(doctor_id: int, start_date: str, end_date: str) -> str:
    """
    Додати відпустку для лікаря.

    :param doctor_id: ID лікаря
    :param start_date: Дата початку (формат YYYY-MM-DD)
    :param end_date: Дата завершення (формат YYYY-MM-DD)
    :return: Повідомлення про успіх або помилку
    """
    try:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return "Невірний формат дати. Використовуйте YYYY-MM-DD."

        if start > end:
            return "Дата початку не може бути пізніше дати завершення."

        sql = text("""
            INSERT INTO vacations (doctor_id, start_date, end_date)
            VALUES (:doctor_id, :start_date, :end_date)
        """)

        with engine.begin() as conn:
            conn.execute(sql, {
                "doctor_id": int(doctor_id),
                "start_date": start_date,
                "end_date": end_date,
            })

        return f"✅ Відпустку додано для лікаря ID {doctor_id}: з {start_date} до {end_date}"

    except Exception as e:
        return f"Помилка додавання відпустки: {str(e)}"


@tool
def delete_vacation_by_dates(doctor_id: int, start_date: str, end_date: str) -> str:
    """
    Видалити відпустку лікаря за датами.
    Не потребує знання vacation_id.

    :param doctor_id: ID лікаря
    :param start_date: Дата початку (формат YYYY-MM-DD)
    :param end_date: Дата завершення (формат YYYY-MM-DD)
    :return: Повідомлення про успіх або помилку
    """
    try:
        # Знаходимо відпустку
        find_query = text("""
            SELECT id FROM vacations
            WHERE doctor_id = :doctor_id
              AND start_date = :start_date
              AND end_date = :end_date
        """)

        with engine.connect() as conn:
            result = conn.execute(find_query, {
                "doctor_id": int(doctor_id),
                "start_date": start_date,
                "end_date": end_date
            })
            row = result.fetchone()

        if not row:
            return f"Відпустку лікаря ID={doctor_id} з {start_date} до {end_date} не знайдено"

        vacation_id = row[0]

        # Видаляємо
        delete_query = text("DELETE FROM vacations WHERE id = :id")
        with engine.begin() as conn:
            conn.execute(delete_query, {"id": vacation_id})

        return f"✅ Відпустку видалено (лікар ID={doctor_id}, {start_date} → {end_date})"

    except Exception as e:
        return f"Помилка видалення: {str(e)}"