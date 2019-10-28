def test(n):

    if n==1:
        return 1
    else:
        return n*test(n-1)