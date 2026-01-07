# Завдання 1
# Напишіть промпт для створення плану навчального
# курсу з певної теми для цільової айдиторії(початківці,
# професіонали, діти, тощо).
# Вхідні параметри: тема, опис цільової аудиторії
# Реалізуйте двома способами:
#  Zero-shot
#  Few-shot

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate, FewShotPromptTemplate


def build_llm() -> GoogleGenerativeAI:
    """Ініціалізація моделі Gemini через LangChain."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не знайдено в .env")

    return GoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=api_key,
        temperature=0.5,
    )


def make_zero_shot_prompt() -> PromptTemplate:
    """Zero-shot: лише інструкція без прикладів."""
    return PromptTemplate.from_template(
        """Ти — професійний методист курсів.

Створи план навчального курсу.
ТЕМА: {topic}
ЦІЛЬОВА АУДИТОРІЯ: {audience}

Структура відповіді:
1) Назва курсу
2) Тривалість (тижні) та формат (онлайн/офлайн/змішаний)
3) Модулі (6–10). Для кожного:
   - Назва модуля
   - Результати навчання (2–3 пункти)
   - Практичне завдання
4) Критерії оцінювання (3–5 пунктів)

Мова: українська."""
    )


def make_few_shot_prompt() -> FewShotPromptTemplate:
    """Few-shot: приклад задає стиль і структуру відповіді."""
    example_prompt = PromptTemplate(
        input_variables=["topic", "audience", "answer"],
        template="ТЕМА: {topic}\nАУДИТОРІЯ: {audience}\nВІДПОВІДЬ:\n{answer}\n",
    )

    # Повний приклад з 6 модулями для ясності
    examples = [
        {
            "topic": "Основи кібербезпеки",
            "audience": "підлітки 13–16 років, без технічної бази",
            "answer": (
                "1) Назва курсу: \"Кібер-Варта\"\n"
                "2) Тривалість та формат: 6 тижнів, онлайн\n"
                "3) Модулі:\n"
                "   1. Паролі та 2FA\n"
                "      - Результати: створює надійні паролі; налаштовує 2FA; знає про менеджери паролів\n"
                "      - Практика: увімкнути 2FA та згенерувати 3 сильні паролі\n"
                "   2. Фішинг і шахрайство\n"
                "      - Результати: розпізнає фішинг; перевіряє посилання; знає правила безпечних покупок\n"
                "      - Практика: проаналізувати 6 прикладів і знайти фішингові ознаки\n"
                "   3. Приватність у соцмережах\n"
                "      - Результати: налаштовує приватність; обмежує доступ до даних; розуміє ризики геолокації\n"
                "      - Практика: налаштувати приватність профілю за чек-листом\n"
                "   4. Шкідливе ПЗ\n"
                "      - Результати: відрізняє типи загроз; перевіряє файли; знає правила оновлень\n"
                "      - Практика: скласти список \"червоних прапорців\" для завантажень\n"
                "   5. Цифрова гігієна\n"
                "      - Результати: формує звички безпеки; розуміє резервні копії; реагує на інциденти\n"
                "      - Практика: створити план цифрової гігієни на тиждень\n"
                "   6. Підсумковий проєкт\n"
                "      - Результати: застосовує правила на практиці; аргументує рішення; працює з чек-листом\n"
                "      - Практика: створити \"інструкцію безпеки\" для однолітків\n"
                "4) Критерії оцінювання:\n"
                "- виконання практичних завдань\n"
                "- мініпідсумки після модулів\n"
                "- фінальний проєкт\n"
                "- активність на заняттях\n"
            ),
        }
    ]

    return FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=(
            "Ти — професійний методист курсів. "
            "Створи план курсу, суворо дотримуючись формату прикладу.\n"
            "Вимога: 6–10 модулів; у кожному 2–3 результати навчання та 1 практичне завдання.\n"
        ),
        suffix="ТЕМА: {topic}\nАУДИТОРІЯ: {audience}\nВІДПОВІДЬ:\n",
        input_variables=["topic", "audience"],
    )


def main() -> None:
    """Точка входу: вводимо тему та аудиторію, друкуємо результати."""
    try:
        llm = build_llm()

        topic = input("Тема курсу: ").strip()
        audience = input("Цільова аудиторія: ").strip()

        if not topic or not audience:
            print("Потрібно вказати тему та аудиторію.")
            return

        print("\n" + "=" * 60)
        print("ZERO-SHOT PROMPTING")
        print("=" * 60 + "\n")

        zero_shot_chain = make_zero_shot_prompt() | llm
        result = zero_shot_chain.invoke({"topic": topic, "audience": audience})
        print(str(result).strip())

        print("\n" + "=" * 60)
        print("FEW-SHOT PROMPTING")
        print("=" * 60 + "\n")

        few_shot_chain = make_few_shot_prompt() | llm
        result = few_shot_chain.invoke({"topic": topic, "audience": audience})
        print(str(result).strip())

    except Exception as exc:
        print(f"Помилка: {exc}")


if __name__ == "__main__":
    main()