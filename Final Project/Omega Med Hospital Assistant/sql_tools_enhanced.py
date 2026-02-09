# sql_tools_enhanced.py - SQL інструменти з покращеним форматуванням
import os
import dotenv
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase
from formatting_utils import (
    format_table_value,
    format_vacation_period,
    format_date_ukrainian,
    format_currency
)

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

engine = create_engine(DATABASE_URL, poolclass=NullPool, future=True)

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
    Повертає відформатовані результати (дати, гроші, телефони).
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

        # Приховуємо ID колонки
        safe_columns = []
        safe_indices = []

        for i, col in enumerate(columns):
            col_lower = col.lower()
            if col_lower == 'id' or col_lower.endswith('_id'):
                continue
            safe_columns.append(col)
            safe_indices.append(i)

        if not safe_columns:
            return "Результати містять тільки службову інформацію (ID)."

        # ✅ ОСОБЛИВИЙ ВИПАДОК: ПЕРІОД ВІДПУСТКИ
        if set(safe_columns) == {'start_date', 'end_date'}:
            periods = []
            for i, row in enumerate(rows, 1):
                start = row[safe_indices[0]]
                end = row[safe_indices[1]]
                formatted_period = format_vacation_period(start, end)
                periods.append(f"{i}. {formatted_period}")

            result_text = "\n".join(periods)
            return f"Знайдено записів: {len(rows)}\n\n{result_text}"

        # ✅ ОДНА КОЛОНКА → НУМЕРОВАНИЙ СПИСОК
        if len(safe_columns) == 1:
            col_name = safe_columns[0]
            items = []
            for i, row in enumerate(rows, 1):
                value = row[safe_indices[0]]
                formatted_value = format_table_value(col_name, value)
                items.append(f"{i}. {formatted_value}")

            result_text = "\n".join(items)
            return f"Знайдено записів: {len(rows)}\n\n{result_text}"

        # ✅ БАГАТО КОЛОНОК → ТАБЛИЦЯ З ФОРМАТУВАННЯМ
        header = " | ".join(safe_columns)
        separator = " | ".join(["---"] * len(safe_columns))

        data_rows = []
        for row in rows:
            formatted_row = []
            for idx in safe_indices:
                col_name = columns[idx]
                value = row[idx]
                formatted_value = format_table_value(col_name, value)
                formatted_row.append(formatted_value)

            data_rows.append(" | ".join(formatted_row))

        table = f"{header}\n{separator}\n" + "\n".join(data_rows)
        return f"Знайдено записів: {len(rows)}\n\n{table}"

    except Exception as e:
        return f"Помилка виконання запиту: {str(e)}"


@tool
def get_doctor_info(doctor_id: int) -> str:
    """
    Отримати повну інформацію про лікаря за ID.
    Включає ПІБ, телефон, зарплату, відділення, спеціалізації.
    """
    try:
        query = text("""
            SELECT 
                d.surname,
                d.name,
                d.patronymic,
                d.phone,
                d.salary,
                d.premium,
                dep.name as department,
                STRING_AGG(DISTINCT s.name, ', ') as specializations
            FROM doctors d
            LEFT JOIN departments dep ON d.department_id = dep.id
            LEFT JOIN doctors_specializations ds ON d.id = ds.doctor_id
            LEFT JOIN specializations s ON ds.specialization_id = s.id
            WHERE d.id = :doctor_id
            GROUP BY d.id, d.surname, d.name, d.patronymic, d.phone, d.salary, d.premium, dep.name
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"doctor_id": doctor_id})
            row = result.fetchone()

        if not row:
            return f"Лікаря з ID={doctor_id} не знайдено"

        full_name = f"{row[0]} {row[1]}"
        if row[2]:
            full_name += f" {row[2]}"

        phone = format_table_value("phone", row[3])
        salary = format_currency(row[4])
        premium = format_currency(row[5]) if row[5] else "немає"
        department = row[6] or "не вказано"
        specializations = row[7] or "не вказано"

        info = f"""
👨‍⚕️ **ПІБ:** {full_name}
📞 **Телефон:** {phone}
💰 **Зарплата:** {salary}
💎 **Премія:** {premium}
🏥 **Відділення:** {department}
📋 **Спеціалізації:** {specializations}
"""
        return info.strip()

    except Exception as e:
        return f"Помилка отримання інформації: {str(e)}"


@tool
def get_doctor_id(name: str = "", surname: str = "") -> str:
    """Знайти ID лікаря за ім'ям та/або прізвищем."""
    try:
        name = (name or "").strip()
        surname = (surname or "").strip()

        if not name and not surname:
            return "Необхідно вказати хоча б ім'я або прізвище"

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
    """Додати відпустку для лікаря."""
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

        formatted_period = format_vacation_period(start_date, end_date)
        return f"✅ Відпустку додано для лікаря ID {doctor_id}: {formatted_period}"

    except Exception as e:
        return f"Помилка додавання відпустки: {str(e)}"


@tool
def delete_vacation_by_dates(doctor_id: int, start_date: str, end_date: str) -> str:
    """Видалити відпустку лікаря за датами."""
    try:
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
            formatted_period = format_vacation_period(start_date, end_date)
            return f"Відпустку лікаря ID={doctor_id} ({formatted_period}) не знайдено"

        vacation_id = row[0]

        delete_query = text("DELETE FROM vacations WHERE id = :id")
        with engine.begin() as conn:
            conn.execute(delete_query, {"id": vacation_id})

        formatted_period = format_vacation_period(start_date, end_date)
        return f"✅ Відпустку видалено (лікар ID={doctor_id}, {formatted_period})"

    except Exception as e:
        return f"Помилка видалення: {str(e)}"
