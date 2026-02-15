from datetime import datetime, date, timedelta


def today_str() -> str:
    return date.today().isoformat()


def now() -> datetime:
    return datetime.utcnow()


def days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


def date_range(start: date, end: date) -> list[str]:
    """Return list of date strings from start to end inclusive."""
    dates = []
    current = start
    while current <= end:
        dates.append(current.isoformat())
        current += timedelta(days=1)
    return dates
