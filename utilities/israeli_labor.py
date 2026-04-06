from datetime import datetime


REGULAR_HOURS_NORMAL = 8 + 35/60
REGULAR_HOURS_SHORT = 7.0
OVERTIME_125_HOURS = 2.0


def is_friday(date_obj):
    return date_obj.weekday() == 4


def calc_overtime_for_day(total_hours, date_str):
    try:
        day = datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        day = None

    regular_limit = REGULAR_HOURS_SHORT if (day and is_friday(day)) else REGULAR_HOURS_NORMAL

    if total_hours <= 0:
        return 0.0, 0.0, 0.0

    regular = min(total_hours, regular_limit)
    remaining = max(0, total_hours - regular_limit)
    ot_125 = min(remaining, OVERTIME_125_HOURS)
    ot_150 = max(0, remaining - OVERTIME_125_HOURS)

    return round(regular, 4), round(ot_125, 4), round(ot_150, 4)


def weighted_hours(regular, ot_125, ot_150):
    return round(regular + ot_125 * 1.25 + ot_150 * 1.5, 4)


def format_hours(h):
    total_minutes = int(round(h * 60))
    hours_int = total_minutes // 60
    minutes = total_minutes % 60
    return f'{hours_int}:{minutes:02d}'
