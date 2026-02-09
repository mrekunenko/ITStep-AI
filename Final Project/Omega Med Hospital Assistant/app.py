# app.py
import dotenv

dotenv.load_dotenv()
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text
from sql_tools import engine
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from agents import get_agent_response, SYSTEM_PROMPT, all_tools

st.set_page_config(
    page_title="Асистент лікарні Омега-Мед",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Асистент адміністратора лікарні Омега-Мед")
st.markdown("Ставте запитання про лікарню, персонал, відділення та відпустки")

# Бічна панель
st.sidebar.markdown("### 🤖 Налаштування")
show_tool_messages = st.sidebar.checkbox("Показувати ToolMessage", value=False)

if st.sidebar.button("🗑 Очистити історію чату", use_container_width=True):
    st.session_state["history"] = [SystemMessage(SYSTEM_PROMPT)]
    st.rerun()

st.sidebar.markdown("---")

if "history" in st.session_state:
    user_messages = sum(1 for msg in st.session_state["history"] if isinstance(msg, HumanMessage))
    st.sidebar.markdown(f"📊 **Запитів у цьому сеансі:** {user_messages}")

st.sidebar.markdown("---")
st.sidebar.markdown(f"🛠 **Інструменти:** {len(all_tools)}")
st.sidebar.markdown("📌 **1** Pinecone | **7** SQL")
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Приклади запитів")

# Розділ з документами
with st.sidebar.expander("📄 Пошук у документах", expanded=False):
    st.caption("General.pdf")
    general_questions = [
        "Яка місія, візія та основні принципи роботи Медичного центру «Омега-Мед»?",
        "Які інформаційні системи використовуються в лікарні та яку роль виконує ЕСОЗ «МедВектор»?",
        "Які заходи інформаційної безпеки та захисту даних застосовуються в Медичному центрі «Омега-Мед»?",
        "Яке медичне обладнання використовується у відділенні діагностики та візуалізації (МРТ, КТ, УЗД)?",
    ]
    for i, q in enumerate(general_questions):
        if st.button(q, key=f"gen_{i}", use_container_width=True):
            st.session_state["selected_question"] = q
            st.rerun()

    st.divider()
    st.caption("For_wokers.docx")
    workers_questions = [
        "Яка тривалість щорічної основної відпустки?",
        "Скільки триває випробувальний термін?",
        "Які надбавки передбачені за роботу у нічний час?",
        "Які права та обов'язки працівника щодо дотримання трудової дисципліни?",
    ]
    for i, q in enumerate(workers_questions):
        if st.button(q, key=f"wrk_{i}", use_container_width=True):
            st.session_state["selected_question"] = q
            st.rerun()

# Розділ з базою даних
with st.sidebar.expander("💾 Перегляд даних", expanded=False):
    if st.button("🧩 Показати схему БД (колонки)", key="db_schema", use_container_width=True):
        st.session_state["selected_question"] = "Покажи схему бази даних"
        st.rerun()

    if st.button("📊 Загальна статистика лікарні", key="hospital_stats", use_container_width=True):
        st.session_state["selected_question"] = "Покажи загальну статистику лікарні"
        st.rerun()

    if st.button("📊 Графік фінансування відділень", key="dept_finance_chart", use_container_width=True):
        st.session_state["show_dept_finance_chart"] = True
        st.rerun()

    # 👥 ЛІКАРІ
    st.markdown("#### 👥 Лікарі")
    doctor_questions = [
        "Покажи список всіх лікарів за алфавітом",
        "Покажи повну інформацію про лікаря Коваленко",
        "Які лікарі працюють у відділенні кардіології?",
        "Скільки лікарів працює в кожному відділенні?",
        "Покажи лікарів із зарплатою вище 80000 грн",
        "Які лікарі мають спеціалізацію хірургія?",
        "Покажи топ-5 лікарів за рівнем зарплати",
        "Які лікарі зараз на відпустці?",
    ]
    for i, question in enumerate(doctor_questions):
        if st.button(question, key=f"data_doctor_{i}", use_container_width=True):
            st.session_state["selected_question"] = question
            st.rerun()

    # 🏥 ВІДДІЛЕННЯ
    st.markdown("#### 🏥 Відділення")
    department_questions = [
        "Які відділення є в лікарні?",
        "Яке відділення має найбільше фінансування?",
        "Покажи відділення з бюджетом менше 600000 грн",
        "Скільки відділень у кожному корпусі?",
        "Яке середнє фінансування відділень?",
    ]
    for i, question in enumerate(department_questions):
        if st.button(question, key=f"data_dept_{i}", use_container_width=True):
            st.session_state["selected_question"] = question
            st.rerun()

    # 🏖 ВІДПУСТКИ
    st.markdown("#### 🏖 Відпустки")
    vacation_questions = [
        "Покажи всі відпустки лікарів",
        "Які відпустки заплановані на березень 2026?",
        "Скільки відпусток у кожного лікаря?",
        "Які лікарі мають відпустку у квітні?",
        "Скільки днів відпустки має лікар Шевченко?",
    ]
    for i, question in enumerate(vacation_questions):
        if st.button(question, key=f"data_vac_{i}", use_container_width=True):
            st.session_state["selected_question"] = question
            st.rerun()

    # 💰 ФІНАНСИ
    st.markdown("#### 💰 Фінанси")
    finance_questions = [
        "Покажи всі донації за сумою (від більшої до меншої)",
        "Який спонсор зробив найбільший внесок?",
        "Скільки донацій отримало кожне відділення?",
        "Яка загальна сума донацій за 2026 рік?",
    ]
    for i, question in enumerate(finance_questions):
        if st.button(question, key=f"data_fin_{i}", use_container_width=True):
            st.session_state["selected_question"] = question
            st.rerun()

    # 🏥 МЕДИЧНІ ДАНІ
    st.markdown("#### 🧬 Медичні дані")
    medical_questions = [
        "Покажи всі палати лікарні за корпусами",
        "Які обстеження проводяться у відділенні кардіології?",
        "Покажи список усіх захворювань за рівнем тяжкості",
        "Які медичні спеціалізації є в лікарні?",
        "Скільки обстежень проводить кожне відділення?",
        "Які захворювання мають найвищий рівень тяжкості?",
    ]
    for i, question in enumerate(medical_questions):
        if st.button(question, key=f"data_med_{i}", use_container_width=True):
            st.session_state["selected_question"] = question
            st.rerun()

    # 🔗 СКЛАДНІ ЗАПИТИ
    st.markdown("#### 🔗 Складні запити")
    complex_questions = [
        "Покажи лікарів разом з їх спеціалізаціями",
        "Покажи лікарів, їх відділення та спеціалізації",
        "Покажи донації зі спонсорами та відділеннями",
        "Які обстеження призначені для конкретних хвороб?",
        "Покажи лікарів разом з їх обстеженнями та відділеннями",
        "Яке відділення отримало найбільше донацій?",
    ]
    for i, question in enumerate(complex_questions):
        if st.button(question, key=f"data_complex_{i}", use_container_width=True):
            st.session_state["selected_question"] = question
            st.rerun()

# Управління відпустками
with st.sidebar.expander("🏖 Управління відпустками", expanded=False):
    if st.button("ℹ️ Інформація про лікаря ID=3", key="doc_info_3", use_container_width=True):
        st.session_state["selected_question"] = "Покажи всю інформацію про лікаря ID=3"
        st.rerun()

    if st.button("📋 Покажи відпустки лікаря ID=3", key="vac_show1", use_container_width=True):
        st.session_state["selected_question"] = "Покажи всі відпустки лікаря ID=3"
        st.rerun()

    if st.button("➕ Додай відпустку 15-25 березня 2026", key="vac_add", use_container_width=True):
        st.session_state["selected_question"] = "Надай відпустку лікарю ID=3 з 2026-03-15 до 2026-03-25"
        st.rerun()

    if st.button("🔍 Покажи відпустки знову", key="vac_show2", use_container_width=True):
        st.session_state["selected_question"] = "Покажи всі відпустки лікаря ID=3"
        st.rerun()

    if st.button("🗑 Видали відпустку 15-25 березня", key="vac_delete", use_container_width=True):
        st.session_state["selected_question"] = "Видали відпустку лікаря ID=3 з 2026-03-15 до 2026-03-25"
        st.rerun()

    if st.button("✅ Покажи відпустки востаннє", key="vac_show3", use_container_width=True):
        st.session_state["selected_question"] = "Покажи всі відпустки лікаря ID=3"
        st.rerun()

# Ініціалізація історії
if "history" not in st.session_state:
    st.session_state["history"] = [SystemMessage(SYSTEM_PROMPT)]

# Вивід чату
for msg in st.session_state["history"]:
    if isinstance(msg, SystemMessage):
        continue

    if isinstance(msg, HumanMessage):
        if str(msg.content).startswith("Виконай цей SQL запит"):
            with st.chat_message("user"):
                st.markdown("📊 Запит даних з бази...")
            continue

        with st.chat_message("user"):
            st.markdown(msg.content)
        continue

    if isinstance(msg, ToolMessage):
        if show_tool_messages:
            with st.chat_message("assistant"):
                st.markdown(f"**ToolMessage ({msg.name})**")
                st.code(msg.content)
        continue

    if isinstance(msg, AIMessage) and msg.content:
        if show_tool_messages or not getattr(msg, "tool_calls", None):
            with st.chat_message("assistant"):
                st.markdown(msg.content)

# Обробка вибраного запитання з кнопок
if "selected_question" in st.session_state:
    user_query = st.session_state.pop("selected_question")
    st.session_state["history"].append(HumanMessage(user_query))

    with st.spinner("🤔 Думаю..."):
        response = get_agent_response(st.session_state["history"])
        st.session_state["history"] = response["messages"]

    st.rerun()

# Блок для графіка фінансування відділень
if st.session_state.get("show_dept_finance_chart"):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT name AS department_name, financing
            FROM departments
            ORDER BY financing DESC
        """))
        rows = result.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["Відділення", "Фінансування"])
        st.subheader("📊 Фінансування відділень")

        fig = px.bar(
            df,
            x="Відділення",
            y="Фінансування",
            text="Фінансування",
            color="Відділення",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(texttemplate="%{text:,.0f} грн", textposition="outside")
        fig.update_layout(
            yaxis_title="Фінансування, грн",
            xaxis_title="Відділення",
            uniformtext_minsize=10,
            uniformtext_mode="hide",
            bargap=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Немає даних про фінансування відділень.")

    # Скидаємо прапорець
    st.session_state["show_dept_finance_chart"] = False

# Поле вводу
user_query = st.chat_input("Напишіть ваше запитання про лікарню...")

if user_query:
    st.session_state["history"].append(HumanMessage(user_query))

    with st.spinner("🤔 Обробляю запит..."):
        response = get_agent_response(st.session_state["history"])
        st.session_state["history"] = response["messages"]

    st.rerun()