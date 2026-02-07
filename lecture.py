from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker
import json

with open("Final Project/Omega-Med_chatbot/credentials.json") as f:
    data = json.load(f)

engine = create_engine(
    f"postgresql+psycopg2://{data['login']}:{data['password']}@localhost:5432/hospital_omegamed"
)

Session = sessionmaker(bind=engine)
metadata = MetaData()
metadata.reflect(bind=engine)

tables = metadata.tables

# ============================================
# 1️⃣ ПЕРЕГЛЯД СТРУКТУРИ ТАБЛИЦЬ І КОЛОНОК
# ============================================
print("=" * 60)
print("СТРУКТУРА ТАБЛИЦЬ:")
print("=" * 60)

for table_name in tables:
    print(f"\n📋 Таблиця: {table_name}")
    print(f"   Колонки: {tables[table_name].columns.keys()}")
    print("-" * 60)

# ============================================
# 2️⃣ ВИКОНАННЯ SELECT ЗАПИТІВ
# ============================================
with Session() as session:
    # Приклад 1: Базовий SELECT з фільтром
    print("\n" + "=" * 60)
    print("1️⃣ SELECT: Лікарі з зарплатою > 120000")
    print("=" * 60)

    query_text = """
    SELECT id, surname, name, salary
    FROM doctors
    WHERE salary > :min_salary
    ORDER BY salary DESC
    """

    query_text = text(query_text)
    result = session.execute(query_text, {"min_salary": 30000})

    # 📊 Отримання назв колонок
    doctors_table = tables['doctors']
    column_names = doctors_table.columns.keys()
    print(f"\nДоступні колонки в таблиці doctors: {list(column_names)}")

    # ============================================
    # 3️⃣ РІЗНІ МЕТОДИ ОТРИМАННЯ РЕЗУЛЬТАТІВ
    # ============================================

    # Метод 1: .all() - всі результати
    results = result.all()
    print(f"\nЗнайдено {len(results)} лікарів:")
    for row in results:
        print(f"   {row.surname} {row.name}: {row.salary}")

    # Приклад 2: .first() - перший результат
    print("\n" + "=" * 60)
    print("2️⃣ .first(): Перший лікар з найвищою зарплатою")
    print("=" * 60)

    query2 = text("SELECT surname, name, salary FROM doctors ORDER BY salary DESC")
    result2 = session.execute(query2)
    first_row = result2.first()
    if first_row:
        print(f"   {first_row.surname} {first_row.name}: {first_row.salary}")

    # Приклад 3: .fetchmany(n) - перші n результатів
    print("\n" + "=" * 60)
    print("3️⃣ .fetchmany(3): Перші 3 відділення")
    print("=" * 60)

    query3 = text("SELECT name, building, financing FROM departments ORDER BY financing DESC")
    result3 = session.execute(query3)
    first_three = result3.fetchmany(3)
    for row in first_three:
        print(f"   {row.name} (Корпус {row.building}): {row.financing}")

    # Приклад 4: Ітерація по результатах (пам'ять-ефективно)
    print("\n" + "=" * 60)
    print("4️⃣ Ітерація: Перші 5 хвороб")
    print("=" * 60)

    query4 = text("SELECT name, severity FROM diseases LIMIT 5")
    result4 = session.execute(query4)
    for i, row in enumerate(result4, 1):
        print(f"   {i}. {row.name} (Тяжкість: {row.severity}/5)")

# ============================================
# ⚠️ БЕЗПЕЧНИЙ INSERT (через параметри)
# ============================================
print("\n" + "=" * 60)
print("5️⃣ Приклад безпечного INSERT (закоментовано)")
print("=" * 60)

print("""
# ✅ ПРАВИЛЬНО (параметризований запит):
with Session() as session:
    insert_query = text('''
        INSERT INTO doctors (surname, name, patronymic, phone, salary)
        VALUES (:surname, :name, :patronymic, :phone, :salary)
    ''')

    session.execute(insert_query, {
        "surname": "Іваненко",
        "name": "Іван",
        "patronymic": "Іванович",
        "phone": "380501234567",
        "salary": 28000
    })
    session.commit()

# ❌ НЕБЕЗПЕЧНО (SQL Injection):
# insert_query = f"INSERT INTO doctors VALUES ('{user_input}')"
""")

print("\n" + "=" * 60)
print("✅ Демонстрація завершена")
print("=" * 60)
