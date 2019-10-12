"""
Charlier

Density:

    a^x/x!          x in {0, 1, ...}

Recurrence:
    -x P_n = a P_{n+1} - (n+a) P_n + n P_{n-1}
    P_{n+1} = (n+a-x)/a P_n - n/a P_{n-1}
"""
