# formatting_utils.py - Утиліти для форматування даних
from datetime import datetime, date
from typing import Any, Optional

# Українські назви місяців
MONTHS_UK = {
    1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
    5: "травня", 6: "червня", 7: "липня", 8: "серпня",
    9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
}


def format_date_ukrainian(date_value: Any) -> str:
    """
    Форматує дату у український формат: "10 березня 2026"
    """
    if date_value is None:
        return "-"

    if isinstance(date_value, str):
        try:
            date_value = datetime.strptime(date_value, "%Y-%m-%d").date()
        except:
            return date_value

    if isinstance(date_value, (date, datetime)):
        day = date_value.day
        month = MONTHS_UK.get(date_value.month, str(date_value.month))
        year = date_value.year
        return f"{day} {month} {year}"

    return str(date_value)


def format_currency(value: Any) -> str:
    """
    Форматує грошову суму: "500 000,00 грн"
    """
    if value is None:
        return "-"

    try:
        num = float(value)
        # Форматування з пробілами як розділювачами тисяч
        formatted = f"{num:,.2f}".replace(",", " ")
        return f"{formatted} грн"
    except:
        return str(value)


def format_phone(phone: str) -> str:
    """
    Форматує телефон: "+380 67 123 4567"
    """
    if not phone or phone == "-":
        return "-"

    phone = phone.replace(" ", "").replace("-", "")

    if phone.startswith("+380") and len(phone) == 13:
        return f"+380 {phone[4:6]} {phone[6:9]} {phone[9:]}"

    return phone


def calculate_days_between(start_date: Any, end_date: Any) -> Optional[int]:
    """
    Розраховує кількість днів між датами
    """
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if isinstance(start_date, (date, datetime)) and isinstance(end_date, (date, datetime)):
            delta = end_date - start_date
            return delta.days + 1  # +1 бо включно
    except:
        pass

    return None


def format_vacation_period(start_date: Any, end_date: Any) -> str:
    """
    Форматує період відпустки з тривалістю
    "з 10 березня по 25 березня 2026 (15 днів)"
    """
    start_uk = format_date_ukrainian(start_date)
    end_uk = format_date_ukrainian(end_date)
    days = calculate_days_between(start_date, end_date)

    if days:
        return f"з {start_uk} по {end_uk} ({days} дн.)"
    else:
        return f"з {start_uk} по {end_uk}"


def get_status_emoji(column_name: str, value: Any) -> str:
    """
    Повертає емодзі для статусу/категорії
    """
    if value is None:
        return "⚪"

    col_lower = column_name.lower()
    val_str = str(value).lower()

    # Фінансування
    if "financing" in col_lower or "фінансування" in val_str:
        try:
            amount = float(value)
            if amount < 300000:
                return "🔴"  # низьке
            elif amount < 700000:
                return "🟡"  # середнє
            else:
                return "🟢"  # високе
        except:
            pass

    # Спеціалізації / відділення
    if "кардіол" in val_str:
        return "💙"
    elif "онкол" in val_str:
        return "🧡"
    elif "хірург" in val_str:
        return "💚"
    elif "реанім" in val_str:
        return "🔴"
    elif "реабіліт" in val_str:
        return "💜"

    # Тяжкість захворювання
    if "severity" in col_lower:
        try:
            sev = int(value)
            if sev >= 8:
                return "🔴"
            elif sev >= 5:
                return "🟡"
            else:
                return "🟢"
        except:
            pass

    return ""


def format_table_value(column_name: str, value: Any) -> str:
    """
    Автоматично форматує значення залежно від типу колонки
    """
    if value is None:
        return "-"

    col_lower = column_name.lower()

    # Дати
    if "date" in col_lower or "дата" in col_lower:
        return format_date_ukrainian(value)

    # Гроші
    if any(word in col_lower for word in ["salary", "financing", "amount", "premium", "зарплат", "фінансув", "сума"]):
        return format_currency(value)

    # Телефон
    if "phone" in col_lower or "телефон" in col_lower:
        return format_phone(str(value))

    # Звичайне значення
    val_str = str(value)[:50]  # обрізка

    # Додати емодзі якщо є
    emoji = get_status_emoji(column_name, value)
    if emoji:
        return f"{emoji} {val_str}"

    return val_str


def format_number_with_spaces(value: Any) -> str:
    """
    Форматує число з пробілами: 1000000 -> "1 000 000"
    """
    try:
        num = int(float(value))
        return f"{num:,}".replace(",", " ")
    except:
        return str(value)
