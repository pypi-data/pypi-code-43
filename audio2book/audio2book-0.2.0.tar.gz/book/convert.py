from datetime import timedelta


def time_to_pages(completed: timedelta, overall: timedelta, pages: int) -> float:
    return (completed / overall) * pages


def str_to_time(time: str) -> timedelta:
    list_time = time.split(':')
    if len(list_time) == 2:
        minutes, seconds = map(lambda x: float(x), list_time)
        hours = 0
    else:
        hours, minutes, seconds = map(lambda x: float(x), list_time)
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def run(completed: str, overall: str, pages: int):
    completed_td = str_to_time(time=completed)
    overall_td = str_to_time(time=overall)
    return time_to_pages(completed_td, overall_td, pages)
