from whattime import TimeType
from whattime import week_info


def test_time_type_state_is_weekday(monday, tuesday, wednesday, thursday, friday, saturday, sunday):
    """ Test week_info is_weekday of given datetime """

    assert week_info(monday).is_weekday is True
    assert week_info(tuesday).is_weekday is True
    assert week_info(wednesday).is_weekday is True
    assert week_info(thursday).is_weekday is True
    assert week_info(friday).is_weekday is True
    assert week_info(saturday).is_weekday is False
    assert week_info(sunday).is_weekday is False


def test_time_type_state_is_weekend(monday, tuesday, wednesday, thursday, friday, saturday, sunday):
    """ Test week_info is_weekday of given datetime """

    assert week_info(monday).is_weekend is False
    assert week_info(tuesday).is_weekend is False
    assert week_info(wednesday).is_weekend is False
    assert week_info(thursday).is_weekend is False
    assert week_info(friday).is_weekend is False
    assert week_info(saturday).is_weekend is True
    assert week_info(sunday).is_weekend is True


def test_time_type_state_certain_day(days, monday, tuesday, wednesday, thursday, friday, saturday,
                                     sunday):
    """ Test week_info days of given datetime """

    for day in days:
        assert week_info(day).is_monday is (day is monday)
        assert week_info(day).is_tuesday is (day is tuesday)
        assert week_info(day).is_wednesday is (day is wednesday)
        assert week_info(day).is_thursday is (day is thursday)
        assert week_info(day).is_friday is (day is friday)
        assert week_info(day).is_saturday is (day is saturday)
        assert week_info(day).is_sunday is (day is sunday)


def test_time_type_state_types(monday, tuesday, wednesday, thursday, friday, saturday, sunday):
    """ Test fitting types for the given datetime """

    assert week_info(monday).types == {TimeType.MONDAY, TimeType.WEEKDAY}
    assert week_info(tuesday).types == {TimeType.TUESDAY, TimeType.WEEKDAY}
    assert week_info(wednesday).types == {TimeType.WEDNESDAY, TimeType.WEEKDAY}
    assert week_info(thursday).types == {TimeType.THURSDAY, TimeType.WEEKDAY}
    assert week_info(friday).types == {TimeType.FRIDAY, TimeType.WEEKDAY}
    assert week_info(saturday).types == {TimeType.SATURDAY, TimeType.WEEKEND}
    assert week_info(sunday).types == {TimeType.SUNDAY, TimeType.WEEKEND}
