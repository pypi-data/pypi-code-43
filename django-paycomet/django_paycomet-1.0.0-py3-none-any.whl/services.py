from django.utils import timezone


def get_card_months():
    months = []

    for x in range(1, 13):
        if x < 10:
            months.append(f'0{x}')
        else:
            months.append(str(x))

    return months


def get_card_years():
    """
    Returns current year plus 20
    """

    years = []
    current_year = timezone.now().year

    for x in range(current_year, current_year + 20):
        last_2_digits = str(x)[2:]
        years.append(last_2_digits)

    return years


def get_amount():
    return '0.01'
