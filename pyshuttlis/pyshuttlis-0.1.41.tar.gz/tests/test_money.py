from shuttlis.money import paisa_to_inr, inr_to_paisa


def test_paisa_to_inr():
    assert paisa_to_inr(2097) == 20.97
    assert paisa_to_inr(208) == 2.08
    assert paisa_to_inr(2090) == 20.9


def test_inr_to_paisa():
    assert inr_to_paisa(20.97) == 2097
    assert inr_to_paisa(20.9) == 2090
    assert inr_to_paisa(2.08) == 208
