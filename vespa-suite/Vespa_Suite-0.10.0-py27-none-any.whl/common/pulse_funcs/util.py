# Python modules
from __future__ import division


def calculate_dwell_time(time_points, duration):
    """
    Given a number of time points and the duration (in milliseconds),
    returns the dwell time (in microseconds).
    """
    return (1000 * duration) / (time_points)


def calculate_duration(time_points, dwell_time):
    """
    Given a number of time points and the dwell time (in microseconds),
    returns the duration (in milliseconds).
    """
    return dwell_time * (time_points) / 1000.0


def check_and_suggest_duration(time_points, 
                               duration, 
                               min_dwell_time, 
                               dwell_time_increment):
    """
    Given a set of time points, the pulse duration, and the machine's 
    minimum dwell time and dwell time increment, evaluates the implied 
    dwell time. Returns the same duration if the implied dwell time is 
    acceptable, otherwise returns a suggested alternate.
    """
    # Calculate the dwell time implied by this combination of
    # time points & duration
    dwell_time = calculate_dwell_time(time_points, duration)

    if dwell_time <= min_dwell_time:
        dwell_time = min_dwell_time
        duration = calculate_duration(time_points, dwell_time)
    else:
        # The implied dwell_time must be equal to the minimum
        # dwell time plus an integer multiple of the dwell time increment.
        dwell_excess = dwell_time - min_dwell_time
        n = dwell_excess // dwell_time_increment
        remainder = dwell_excess % dwell_time_increment
        diff = remainder
        if diff > 0.5*dwell_time_increment:
            diff = dwell_time_increment - remainder

        if diff < 0.000001:
            # Close enough, no change needed
            pass
        else:
            # Nudge the dwell_time a little
            n = n + 1

            dwell_time = min_dwell_time + n * dwell_time_increment

            duration = calculate_duration(time_points, dwell_time)

    return duration


def check_dwell_time(dwell_time, min_dwell_time, dwell_time_increment):
    """ 
    Performs two checks on dwell time: 
    First, make sure dwell_time > min_dwell_time
    Second, make sure dwell_time = min_dwell_time + N*dwell_time_increment
    where N is an integer.
    """
    
    if dwell_time < min_dwell_time:
        return "The dwell time (%f) is less than the minimum dwell time "   \
               "(%f) specified in the machine settings." %                  \
               (dwell_time, min_dwell_time)
    else:
        # The dwell_time must be equal to the minimum dwell time 
        # plus an integer multiple of the dwell time increment.
        dwell_excess = dwell_time - min_dwell_time
        n = dwell_excess // dwell_time_increment
        remainder = dwell_excess % dwell_time_increment
        diff = remainder
        if diff > 0.5*dwell_time_increment:
            diff = dwell_time_increment - remainder

        if diff > 0.000001:
            return "The dwell time must be equal to the minimum dwell (%f) " \
                   "time plus an integer multiple of the dwell time "        \
                   "increment (%f) specified in the machine settings." %     \
                   (min_dwell_time, dwell_time_increment)
        
    return ''
