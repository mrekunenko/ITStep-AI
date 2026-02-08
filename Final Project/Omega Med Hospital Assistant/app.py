# app.py
import dotenv

dotenv.load_dotenv()

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from agents import get_agent_response, SYSTEM_PROMPT

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
st.sidebar.markdown("🛠 **Інструменти:** 6")
st.sidebar.markdown("📌 **1** Pinecone | **5** SQL")
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

    sql_questions = [
        "Покажи список всіх лікарів",
        "Які відділення є в лікарні?",
        "Покажи всі палати лікарні",
        "Покажи перелік обстежень",
        "Покажи список захворювань",
        "Покажи перелік медичних спеціалізацій",
        "Покажи всі відпустки лікарів",
        "Покажи всі донації",
        "Покажи всіх спонсорів лікарні",
        "Покажи лікарів разом з їх спеціалізаціями",
        "Покажи лікарів та їх відділення",
        "Покажи лікарів разом з їх обстеженнями",
        "Покажи донації разом зі спонсорами та відділеннями",
        "Покажи обстеження разом з хворобами та відділеннями",
    ]

    for i, question in enumerate(sql_questions):
        if st.button(question, key=f"data_sql_{i}", use_container_width=True):
            st.session_state["selected_question"] = question
            st.rerun()

# Управління відпустками
with st.sidebar.expander("🏖 Управління відпустками", expanded=False):
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

# Поле вводу
user_query = st.chat_input("Напишіть ваше запитання про лікарню...")

if user_query:
    st.session_state["history"].append(HumanMessage(user_query))

    with st.spinner("🤔 Обробляю запит..."):
        response = get_agent_response(st.session_state["history"])
        st.session_state["history"] = response["messages"]

    st.rerun()