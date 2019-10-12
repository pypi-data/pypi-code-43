"""
Meixner

Density:
    Gamma(b+x)/(Gamma(b) x!) c^x    x in {0, 1, ...}

Recurrence:
    (c-1) x P_n = c (n+b) P_{n+1} - (n + (n+b)c) P_n + n P_{n-1}
    c (n+b) P_{n+1} = (n + (n+b)c - (c-1)x) P_n + n P_{n-1}
    P_{n+1} = (n+(n+b)c-(c-1)x)/(c(n+b)) P_n n/(c(n+b)) P_{n-1}
"""
