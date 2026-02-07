#sql_tools.py
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase

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

# підключення до Supabase через NullPool
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    future=True,
)

# створення SQLDatabase
try:
    import streamlit as st


    @st.cache_resource
    def get_sql_db():
        return SQLDatabase(engine)


    db = get_sql_db()
except Exception:
    db = SQLDatabase(engine)


def _strip_one_statement(q: str) -> str:
    q = (q or "").strip()
    if q.endswith(";"):
        q = q[:-1].strip()
    return q


def _is_single_select(q: str) -> bool:
    if not q:
        return False
    if ";" in q:
        return False
    return q.upper().startswith("SELECT")


@tool
def show_db_schema() -> str:
    """Show database schema with tables and columns from public schema."""
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
    Execute a SELECT query on the hospital database.
    Returns formatted results as a table or list.
    Use this for viewing data about doctors, departments, examinations, donations, vacations.
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
            columns = result.keys()

            if not rows:
                return "Запит виконано, але результатів не знайдено."

            # Форматування як markdown таблиця
            header = " | ".join(columns)
            separator = " | ".join(["---"] * len(columns))
            data_rows = []

            for row in rows:
                formatted_row = []
                for val in row:
                    if val is None:
                        formatted_row.append("-")
                    else:
                        formatted_row.append(str(val))
                formatted_row = [str(v)[:50] for v in formatted_row]  # Обрізка довгих значень
                data_rows.append(" | ".join(formatted_row))

            table = f"{header}\n{separator}\n" + "\n".join(data_rows)
            return f"Знайдено записів: {len(rows)}\n\n{table}"

    except Exception as e:
        return f"Помилка виконання запиту: {str(e)}"

@tool
def add_vacation(doctor_id: int, start_date: str, end_date: str) -> str:
    """Add vacation for doctor with given ID."""
    try:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return "Невірний формат дати. Використовуйте YYYY-MM-DD."

        if start > end:
            return "Дата початку не може бути пізніше дати завершення."

        sql = text(
            """
            INSERT INTO vacations (doctor_id, start_date, end_date)
            VALUES (:doctor_id, :start_date, :end_date)
            """
        )

        with engine.begin() as conn:
            conn.execute(
                sql,
                {
                    "doctor_id": int(doctor_id),
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )

        return f"Відпустку додано для лікаря ID {doctor_id}: з {start_date} до {end_date}"

    except Exception as e:
        return f"Помилка додавання відпустки: {str(e)}"


@tool
def delete_vacation(vacation_id: int) -> str:
    """Delete vacation by ID."""
    try:
        sql = text("DELETE FROM vacations WHERE id = :vacation_id")

        with engine.begin() as conn:
            result = conn.execute(sql, {"vacation_id": int(vacation_id)})

        if result.rowcount == 0:
            return f"Відпустку з ID={vacation_id} не знайдено"

        return f"Відпустку ID={vacation_id} видалено"

    except Exception as e:
        return f"Помилка видалення: {str(e)}"