# Завдання 1
# Напишіть модель для генерації персонального плану
# тренувань з двох ланцюгів:
#  Перший ланцюг отримує мету тренування(схуднення,
# набір м’язів, тощо) та повертає список вправ
#  Другий ланцюг отримує список вправ, рівень
# підготовки користувача(низький, середній,
# професіонал) та кількість часу на тиждень(в годинах)
# і повертає план тренувань

import os
from typing import List, Literal
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# --------- LLM ---------
def build_llm() -> GoogleGenerativeAI:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY не знайдено в .env")

    return GoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=api_key,
        temperature=0.4,
    )


# --------- Chain 1: goal -> exercises ---------
class ExercisesOut(BaseModel):
    exercises: List[str] = Field(
        min_length=6,
        max_length=12,
        description="Список вправ під мету тренувань"
    )


def build_exercises_chain(llm: GoogleGenerativeAI):
    parser = PydanticOutputParser(pydantic_object=ExercisesOut)

    prompt = PromptTemplate.from_template(
        """Ти — сертифікований фітнес-тренер.
За метою тренування підбери список вправ.

МЕТА: {goal}

Вимоги:
- Поверни 6–12 вправ (рядки), без повторів
- Вправи мають бути реалістичні для звичайного залу або дому
- Мова: українська

{format_instructions}
""",
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


# --------- Chain 2: exercises + level + hours -> weekly plan ---------
Level = Literal["низький", "середній", "професіонал"]


class PlanDay(BaseModel):
    day: str = Field(description="День тижня або назва дня")
    session: str = Field(
        description="Опис тренування на цей день (вправи, підходи/повтори або час)"
    )
    est_minutes: int = Field(
        ge=10,
        le=180,
        description="Оцінка тривалості тренування в хвилинах"
    )


class TrainingPlanOut(BaseModel):
    total_week_minutes: int = Field(
        ge=60,
        description="Сумарні хвилини тренувань на тиждень"
    )
    days: List[PlanDay] = Field(
        min_length=2,
        max_length=6,
        description="План по днях тижня"
    )


def build_plan_chain(llm: GoogleGenerativeAI):
    parser = PydanticOutputParser(pydantic_object=TrainingPlanOut)

    prompt = PromptTemplate.from_template(
        """Ти — персональний фітнес-тренер.
Склади тижневий план тренувань на основі списку вправ.

ВХІДНІ ДАНІ:
- Вправи: {exercises}
- Рівень підготовки: {level}
- Доступний час на тиждень (год): {hours}

Правила:
- Розподіли навантаження на 2–6 тренувальних днів
- Для кожного дня: короткий опис сесії + оцінка тривалості (est_minutes)
- Сумарний час за тиждень НЕ перевищує {week_minutes} хвилин
- Якщо часу мало — обери найважливіші вправи і скороти обсяг
- Мова: українська

{format_instructions}
""",
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    return prompt | llm | parser


def normalize_level(raw: str) -> str:
    """Нормалізація введеного рівня до стандартного формату."""
    value = raw.strip().lower()
    mapping = {
        "низький": "низький",
        "низкий": "низький",
        "початковий": "низький",
        "новачок": "низький",
        "середній": "середній",
        "средний": "середній",
        "професіонал": "професіонал",
        "профессионал": "професіонал",
        "просунутий": "професіонал",
    }
    return mapping.get(value, value)


def main() -> None:
    """Головна функція: зв'язує два ланцюги для створення плану тренувань."""
    try:
        llm = build_llm()
    except ValueError as e:
        print(e)
        return

    # Вхідні дані
    goal = input("🎯 Мета тренування (схуднення/набір м'язів/витривалість): ").strip()
    level_raw = input("🏋️ Рівень (низький/середній/професіонал): ").strip()
    hours_raw = input("⏱️ Годин на тиждень (наприклад 3.5): ").strip()

    if not goal:
        print("❌ Мета не може бути порожньою.")
        return

    level = normalize_level(level_raw)
    if level not in ("низький", "середній", "професіонал"):
        print("❌ Рівень має бути: низький / середній / професіонал")
        return

    try:
        hours = float(hours_raw.replace(",", "."))
        if hours <= 0:
            raise ValueError
    except ValueError:
        print("❌ Години мають бути числом > 0 (наприклад 2 або 3.5)")
        return

    week_minutes = int(round(hours * 60))

    # Chain 1: генерація вправ
    print("\n🔄 Генерую список вправ...")
    try:
        exercises_chain = build_exercises_chain(llm)
        ex_out: ExercisesOut = exercises_chain.invoke({"goal": goal})
    except Exception as e:
        print(f"❌ Помилка генерації вправ: {e}")
        return

    print("\n✅ Список вправ:")
    for i, ex in enumerate(ex_out.exercises, start=1):
        print(f"  {i}. {ex}")

    # Chain 2: генерація плану
    print("\n🔄 Складаю тижневий план...")
    try:
        plan_chain = build_plan_chain(llm)
        plan_out: TrainingPlanOut = plan_chain.invoke({
            "exercises": ex_out.exercises,
            "level": level,
            "hours": hours,
            "week_minutes": week_minutes,
        })
    except Exception as e:
        print(f"❌ Помилка генерації плану: {e}")
        return

    print("\n📅 План тренувань на тиждень:")
    for day in plan_out.days:
        print(f"\n• {day.day} (~{day.est_minutes} хв)")
        print(f"  {day.session}")

    print(f"\n⏱️ Разом: {plan_out.total_week_minutes} хв (ліміт: {week_minutes} хв)")


if __name__ == "__main__":
    main()