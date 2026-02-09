# Асистент адміністратора лікарні Омега-Мед

ReAct агент на базі LangGraph з RAG та SQL інструментами.

## Технології
- **LLM**: Google Gemini 2.5 Flash
- **Фреймворк**: LangChain + LangGraph
- **Векторна БД**: Pinecone
- **Реляційна БД**: PostgreSQL (Supabase)
- **Інтерфейс**: Streamlit

## Встановлення

```bash
pip install -r requirements.txt

```

Створіть `.env`:
```env
GEMINI_API_KEY=your_key
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=omegamed-v3
PINECONE_NAMESPACE=default
DB_USER=your_user
SUPABASE_DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=6543

```

Завантажте документи:
```bash
python upload_docs_to_pinecone.py
```

Запустіть:
```bash
streamlit run app.py
```

## Функціонал

🔍 Пошук у документах (PDF/DOCX)
📊 Повна статистика лікарні (лікарі, відділення, обстеження 2026)
👨‍⚕️ Управління лікарями (ID за ПІБ, повна інформація)
🏥 Запити до БД (відділення, палати, донати)
📅 Відпустки: додавання/видалення за датами (без ID!)
📋 30 видів обстежень з датами

## Інструменти

search_policy_docs - RAG пошук у доках
run_sql_query - SELECT з форматуванням
get_doctor_id - знаходить ID за ПІБ
get_doctor_info - повна картка лікаря
get_hospital_stats - статистика (8 показників)
add_vacation - додавання відпустки
delete_vacation_by_dates - видалення за датами
show_db_schema - схема БД

