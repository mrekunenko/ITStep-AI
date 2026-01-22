# Модуль 3. Generative AI, LLM
# Тема: Langchain. Частина 7
# Завдання 1
# Напишіть додаток з чат ботом по допомозі з вивченням
# англійської мови.
#  Якщо користувач просить перекласти слово або
# фразу, то вивести переклад та приклад використання
# у речені
#  Якщо користувач просить перекласти речення, то
# вивести переклад та пояснення граматики, наприклад
# структура there is/are, пасивна форма дієслова, тощо

import re
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ---------------- UI ----------------
st.set_page_config(page_title="English Helper", page_icon="📘")
st.title("📘 English Helper Chat")

api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("⚠️ Додайте GEMINI_API_KEY у secrets")
    st.stop()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    api_key=api_key,
    temperature=0.5,
)


# ---------------- Logic ----------------
def detect_request_kind(text: str) -> str:
    """
    Returns: 'word_phrase' | 'sentence'
    Heuristic:
      - sentence: has ending punctuation OR 4+ words OR has verb-like patterns
      - word_phrase: otherwise
    """
    t = text.strip()

    if re.search(r"\b(translate|переклади|перекласти)\b.*\b(sentence|речення)\b", t, re.I):
        return "sentence"

    words = re.findall(r"[A-Za-z']+", t)
    word_count = len(words)
    has_punct = bool(re.search(r"[.!?…]$", t))
    has_clause = bool(re.search(r"\b(there is|there are|was|were|is|are|am|have|has|do|does|did)\b", t, re.I))

    if has_punct or word_count >= 4 or has_clause:
        return "sentence"
    return "word_phrase"


SYSTEM_BASE = SystemMessage(
    "Ти дружній тьютор з англійської. Пиши коротко, чітко, структуровано. "
    "Якщо інформації недостатньо — постав 1 уточнююче питання."
)

SYSTEM_WORD_PHRASE = SystemMessage(
    "ЗАДАЧА: користувач просить переклад слова/фрази.\n"
    "Відповідь формату:\n"
    "1) Переклад (UA)\n"
    "2) 1-2 приклади англійською з перекладом\n"
    "3) (Опційно) синонім або типова колокація\n"
    "Не давай довгих лекцій."
)

SYSTEM_SENTENCE = SystemMessage(
    "ЗАДАЧА: користувач просить переклад речення.\n"
    "Відповідь формату:\n"
    "1) Переклад (UA)\n"
    "2) Пояснення граматики (2-5 пунктів): час, порядок слів, there is/are, passive, модальні, артиклі тощо\n"
    "3) 1 короткий варіант-перефраз англійською (опційно)\n"
    "Пояснюй просто, як для новачка."
)


def get_response(user_text: str) -> str:
    kind = detect_request_kind(user_text)
    system_msg = SYSTEM_SENTENCE if kind == "sentence" else SYSTEM_WORD_PHRASE

    # Додати останні 6 повідомлень для контексту діалогу
    context = st.session_state.chat[-6:] if len(st.session_state.chat) > 1 else []
    messages = [SYSTEM_BASE, system_msg] + context + [HumanMessage(user_text)]

    return llm.invoke(messages).content


# ---------------- State ----------------
if "chat" not in st.session_state:
    st.session_state.chat = [
        AIMessage("Привіт! Надішли слово/фразу або речення англійською — допоможу з перекладом 🙂")
    ]

# Render chat
for msg in st.session_state.chat:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

# Input
if user_input := st.chat_input("Напиши слово/фразу або речення англійською…"):
    st.session_state.chat.append(HumanMessage(user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    answer = get_response(user_input)
    st.session_state.chat.append(AIMessage(answer))
    with st.chat_message("assistant"):
        st.markdown(answer)