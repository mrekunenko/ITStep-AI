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

- Пошук у документах лікарні (PDF/DOCX)
- Запити до БД (лікарі, відділення, обстеження)
- Управління відпустками
- Перегляд схеми БД

## Інструменти

1. `search_policy_docs` - RAG пошук
2. `run_sql_query` - SELECT запити
3. `add_vacation` - додавання відпустки
4. `delete_vacation` - видалення відпустки
5. `show_db_schema` - структура БД
