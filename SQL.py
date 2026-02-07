from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker
import json

# Читаємо credentials
with open('credentials.json') as file:
    data = json.load(file)
    password = data['password']

# Дані підключення до Supabase
HOST = "aws-1-eu-north-1.pooler.supabase.com"
PORT = "5432"
DATABASE = "postgres"
USERNAME = "postgres.ycuzqizjggpnswrhhvjk"

DATABASE_URL = f"postgresql+psycopg2://{USERNAME}:{password}@{HOST}:{PORT}/{DATABASE}"

# Створення підключення
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Отримання всіх таблиць
metadata = MetaData()
metadata.reflect(bind=engine)

print(f"Знайдено таблиць: {len(metadata.tables)}\n")

# for table_name in metadata.tables:
#     table = metadata.tables[table_name]
#     print(f"Таблиця: {table_name}")
#     print(f"Колонки: {[col.name for col in table.columns]}")
#     print('-'*50)


query_text = """
SELECT *
FROM DOCTORS
"""

query_text = text(query_text)

query = session.execute(query_text)

# print(query)

result = query.fetchall()

# print(result)
for row in result:
    print(row)

