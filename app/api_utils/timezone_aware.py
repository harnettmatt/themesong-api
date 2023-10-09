from datetime import datetime, timezone


def self_aware_datetime(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc)
