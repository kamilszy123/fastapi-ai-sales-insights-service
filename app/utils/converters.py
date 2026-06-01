from datetime import datetime
from decimal import Decimal, InvalidOperation


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None


def parse_datetime(value):
    if not value:
        return None
    # change ISO8601 'Z' for +00:00
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
