"""
..
  PYTEST_DONT_REWRITE
"""

# Timer used for the warmup budget and the timer precision timeout. Not used when
# measuring the test function. Must return elapsed real time in seconds - the budgets are
# compared against --benchmark-max-time, so the unit is part of the contract.
# Monotonic, so that a clock adjustment can't stretch or cut a budget.
from time import monotonic as timeout_timer

try:
    from __pypy__.time import CLOCK_MONOTONIC  # type: ignore
    from __pypy__.time import clock_gettime  # type: ignore

    def monotonic():
        return clock_gettime(CLOCK_MONOTONIC)

except ImportError:
    from timeit import default_timer
else:
    default_timer = monotonic


def compute_timer_precision(timer, timeout_timer=timeout_timer):
    precision = None
    points = 0
    timeout = timeout_timer() + 1.0
    previous = timer()
    # Stop as soon as we have enough data points or the timeout expires.
    while timeout_timer() < timeout and points < 100:
        for _ in range(10):
            t1 = timer()
            t2 = timer()
            dt = t2 - t1
            if 0 < dt:
                break
        else:
            dt = t2 - previous
            if dt <= 0.0:
                continue
        if precision is not None:
            precision = min(precision, dt)
        else:
            precision = dt
        points += 1
        previous = timer()
    return precision
