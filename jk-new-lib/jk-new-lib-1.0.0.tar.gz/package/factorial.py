"""
Liczę
"""


def factorial(number):
    result = 1
    for i in range(2, number + 1):
        result *= i
    return result


assert factorial(5) == 120, 'FAILED'
print('PASS')
assert factorial(10) == 292928, 'FAILED'


