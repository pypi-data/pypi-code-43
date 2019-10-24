import datetime

def estimate_time_remaining(prev_time, curr_time, steps_between, current_step, total_steps):
    remaining_steps = total_steps - current_step
    time_elapsed = curr_time - prev_time
    if steps_between == 0:
        time_elapsed_per_step = datetime.timedelta(seconds=0)
    else:
        time_elapsed_per_step = time_elapsed / steps_between
    time_remaining = remaining_steps * time_elapsed_per_step
    return datetime.timedelta(seconds=time_remaining.seconds)

def estimate_time_remaining_with_history(
    prev_time, curr_time, steps_between, current_step, total_steps,
    history, max_history
):
    remaining_steps = total_steps - current_step
    time_elapsed = curr_time - prev_time
    if steps_between == 0:
        time_elapsed_per_step = datetime.timedelta(seconds=0)
    else:
        time_elapsed_per_step = time_elapsed / steps_between

    if len(history) > max_history:
        history.pop(0)
    history.append(time_elapsed_per_step)
    ave = sum([td.microseconds for td in history]) / len(history)
    time_remaining = remaining_steps * ave
    remaining = datetime.timedelta(microseconds=time_remaining)
    return datetime.timedelta(seconds=remaining.seconds), history
