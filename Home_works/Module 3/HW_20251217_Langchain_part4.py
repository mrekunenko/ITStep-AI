# Завдання 1
# Напишіть чат модель яка підсумовує всю розмову в
# декілька речень. Вкажіть щоб модель зберігала якомога
# більше деталей.
# Використайте цю модель для простого чат бота який
# замість trim_massages використовує модель з підсумуванням.
# Підсумовуйте повідомлення, коли їх більше 4.
# Старі повідомлення треба видалити
# НЕ ВИДАЛЯТИ SystemMessage та не використовувати
# його для підсумування

import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate


# -------------------- LLM --------------------
def build_llm() -> ChatGoogleGenerativeAI:
    """Створює чат-модель Gemini."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY не знайдено в .env")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=api_key,
        temperature=0.4,
    )


# -------------------- Summarizer --------------------
class SummaryOut(BaseModel):
    summary: str = Field(
        description="Підсумок розмови у кількох реченнях з максимальною кількістю деталей"
    )


def build_summarizer_chain(llm: ChatGoogleGenerativeAI):
    """
    Ланцюг підсумовування.
    ВАЖЛИВО: SystemMessage не включаємо у текст для підсумку.
    """
    parser = PydanticOutputParser(pydantic_object=SummaryOut)

    prompt = PromptTemplate.from_template(
        """Ти — модель для підсумовування діалогу.

Підсумуй розмову у 2–4 реченнях, зберігаючи якомога більше важливих деталей:
- Факти, числа, дати, імена
- Наміри та запити користувача
- Домовленості та рішення
- Конкретні приклади

Не додавай нічого від себе і не вигадуй.
Не пиши, хто саме що сказав (без "користувач/бот"), просто стисла сутність.

ДІАЛОГ (лише Human/AI повідомлення):
{conversation}

{format_instructions}
""",
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


# -------------------- Helpers --------------------
def count_non_system_messages(messages: List[BaseMessage]) -> int:
    """Рахує тільки HumanMessage та AIMessage (SystemMessage не враховуємо)."""
    return sum(isinstance(m, (HumanMessage, AIMessage)) for m in messages)


def conversation_to_text(messages: List[BaseMessage]) -> str:
    """
    Перетворює історію на текст для підсумовування.
    SystemMessage НЕ включаємо.
    """
    lines: List[str] = []
    for m in messages:
        if isinstance(m, HumanMessage):
            lines.append(f"Human: {m.content}")
        elif isinstance(m, AIMessage):
            lines.append(f"AI: {m.content}")
    return "\n".join(lines)


def create_summary_history(messages: List[BaseMessage], summary: str) -> List[BaseMessage]:
    """
    Залишає SystemMessage і додає AIMessage з підсумком.
    Видаляє всі старі Human/AI повідомлення.
    """
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    system_msg = system_msgs[0] if system_msgs else SystemMessage(
        "Ти — ввічливий чат-бот."
    )

    return [
        system_msg,
        AIMessage(content=f"Підсумок попередньої розмови: {summary}"),
    ]


# -------------------- Main chat --------------------
def main() -> None:
    """Чат-бот з автоматичним підсумовуванням після 4 повідомлень."""
    try:
        llm = build_llm()
        summarizer = build_summarizer_chain(llm)
    except ValueError as e:
        print(e)
        return

    messages: List[BaseMessage] = [
        SystemMessage(
            "Ти — ввічливий чат-бот. Відповідай коротко, логічно та по суті українською."
        )
    ]

    print("🤖 Чат-бот з автопідсумовуванням")
    print("Для виходу — порожній рядок\n")

    while True:
        user_text = input("Human: ").strip()
        if not user_text:
            break

        messages.append(HumanMessage(content=user_text))

        # Відповідь бота
        try:
            ai_msg = llm.invoke(messages)
            messages.append(ai_msg)
            print(f"AI: {ai_msg.content}\n")
        except Exception as e:
            print(f"❌ Помилка генерації відповіді: {e}\n")
            messages.pop()  # Видаляємо Human повідомлення
            continue

        # Підсумовування після 4 Human+AI повідомлень
        if count_non_system_messages(messages) > 4:
            print("🔄 Підсумовую розмову...")

            try:
                convo_text = conversation_to_text(messages)
                summary_out: SummaryOut = summarizer.invoke({"conversation": convo_text})

                print(f"📝 Підсумок: {summary_out.summary}\n")

                messages = create_summary_history(messages, summary_out.summary)
                print("✅ Старі повідомлення видалено (SystemMessage збережено)\n")

            except Exception as e:
                print(f"⚠️ Помилка підсумовування: {e}. Продовжую без підсумку.\n")


if __name__ == "__main__":
    main()