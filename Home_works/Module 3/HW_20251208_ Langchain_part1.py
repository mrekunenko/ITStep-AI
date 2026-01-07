# Завдання 1
# Прочитайте файл data\lesson9\return_policy.txt Та
# напишіть простий чат бот для відповідей на питання
# користувачів стосовно повернення товару. Діалог завершується
# коли користувач вводить порожній рядок.
# Передавайте усю історію спілкування у форматі:
# Instruction: ….
# Human: massage1
# AI: message2
# Human: massage3
# AI: message4
# Human: massage5
# AI:

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI


def load_return_policy(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def main() -> None:
    load_dotenv()

    llm = GoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.6,
    )

    policy = load_return_policy("data/lesson9/return_policy.txt")

    instruction = f"""Instruction:
Ти — чат-бот служби підтримки магазину.
Відповідай виключно на основі правил повернення товару, наведених нижче.
Якщо запит не стосується повернення товару — повідом, що не можеш надати відповідь.

Правила повернення товару:
{policy}
"""

    history = instruction

    print("Чат-бот з питань повернення товару")
    print("Натисніть Enter без тексту для завершення діалогу.\n")

    while True:
        user_message = input("Human: ").strip()
        if not user_message:
            break

        history += f"\nHuman: {user_message}\nAI:"
        response = str(llm.invoke(history)).strip()
        history += f" {response}"

        print(f"AI: {response}\n")

    print("\nПовна історія діалогу:\n")
    print(history)


if __name__ == "__main__":
    main()
