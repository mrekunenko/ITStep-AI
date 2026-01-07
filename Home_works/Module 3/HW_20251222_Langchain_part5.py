# Завдання 1
# Напишіть чат бота, з інструментом по рекомендації
# ресторанів.
# Для цього скористайтесь
# GoogleSerperAPIWrapper(type="places")
# Інструмент повинен отримувати запит для пошуку та
# повертати таку інформацію про ресторани:
#  назва
#  посилання на сайт(якщо є)
#  рейтинг
# Більш детально дивись документацію

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

# Глобальний searcher для уникнення повторної ініціалізації
_places_searcher: Optional[GoogleSerperAPIWrapper] = None


def build_llm() -> ChatGoogleGenerativeAI:
    """Ініціалізація LLM (Gemini) для агента."""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("❌ GEMINI_API_KEY не знайдено в .env")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        api_key=gemini_api_key,
        temperature=0.3,
    )


def build_places_search() -> GoogleSerperAPIWrapper:
    """Ініціалізація Serper Places пошуку."""
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        raise ValueError("❌ SERPER_API_KEY не знайдено в .env")

    return GoogleSerperAPIWrapper(
        serper_api_key=serper_api_key,
        type="places",
    )


def _safe_float(value: Any) -> Optional[float]:
    """Безпечна конвертація у float."""
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def get_restaurants(query: str) -> List[Dict[str, Any]]:
    """
    Інструмент для агента: шукає ресторани через Serper Places API.

    Args:
        query: Пошуковий запит (наприклад: "піцерія Київ", "суші Львів центр")

    Returns:
        Список словників з інформацією про ресторани:
        [
            {"name": "...", "website": "..." | None, "rating": 4.6 | None},
            ...
        ]
    """
    global _places_searcher

    # Ініціалізуємо searcher один раз
    if _places_searcher is None:
        try:
            _places_searcher = build_places_search()
        except ValueError as e:
            return [{"name": str(e), "website": None, "rating": None}]

    # Виконуємо пошук
    try:
        data = _places_searcher.results(query)
    except Exception as e:
        return [{"name": f"Помилка пошуку: {e}", "website": None, "rating": None}]

    places = data.get("places", [])

    if not places:
        return [{"name": "Ресторани не знайдено", "website": None, "rating": None}]

    # Формуємо результати
    results: List[Dict[str, Any]] = []
    for place in places[:8]:
        rating = _safe_float(place.get("rating"))
        results.append({
            "name": place.get("title") or "Без назви",
            "website": place.get("website"),
            "rating": rating,
        })

    return results


def main() -> None:
    """Чат-бот для рекомендації ресторанів з використанням Serper Places API."""
    # Завантажуємо .env один раз на початку
    load_dotenv()

    try:
        llm = build_llm()
    except ValueError as exc:
        print(exc)
        return

    agent = create_react_agent(
        model=llm,
        tools=[get_restaurants],
    )

    messages = [
        SystemMessage(
            "Ти — чат-бот для рекомендації ресторанів.\n"
            "Завжди використовуй інструмент get_restaurants для пошуку.\n"
            "Якщо користувач не вказав місто/район/локацію — постав 1 уточнювальне питання.\n"
            "Після отримання результатів інструмента виведи нумерований список.\n"
            "Для кожного ресторану покажи рівно ці поля:\n"
            "- Назва\n"
            "- Рейтинг (якщо rating є None — напиши 'немає')\n"
            "- Сайт (якщо website є None — напиши 'немає')\n"
            "Не вигадуй рейтинг або сайт, використовуй лише ті дані, що повернув інструмент.\n"
            "Мова: українська."
        )
    ]

    print("🍽️ Бот рекомендацій ресторанів")
    print("Приклад: 'знайди піцерію у Києві' або 'суші у Львові'")
    print("Для виходу — порожній рядок\n")

    while True:
        user_text = input("Ви: ").strip()
        if not user_text:
            break

        messages.append(HumanMessage(user_text))

        try:
            response = agent.invoke({"messages": messages})
            messages = response["messages"]

            # Виводимо останню відповідь агента
            print(f"\nБот:\n{messages[-1].content}\n")

        except Exception as exc:
            print(f"❌ Помилка: {exc}\n")


if __name__ == "__main__":
    main()