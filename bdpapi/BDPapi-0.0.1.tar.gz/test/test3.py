def nthUglyNumber(n):
    cnt = 1
    num = 1
    while n != cnt:
        num += 1
        if num % 2 == 0 or num % 3 == 0 or num % 5 == 0:
            cnt += 1
    return num


# write your code here


# write your code here

print(nthUglyNumber(41))
