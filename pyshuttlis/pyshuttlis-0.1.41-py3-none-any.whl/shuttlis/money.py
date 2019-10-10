def paisa_to_inr(amount_in_paisa: int):
    return round(amount_in_paisa / 100, ndigits=2)


def inr_to_paisa(amount_in_inr: int):
    return int(amount_in_inr * 100)
