def div(a, b):
    return a / b

"""
sbsjkbs
"""

assert div(3, 6) == 0.5, "FAILED_1"
print("PASSED_1")

assert (div(3, 1) + div(-4, 2)) == 1.00, "FAILED_2"
print("PASSED_2")

assert div(8, 4) == 2, "FAILED_3"
print("PASSED_3")
try:
    div(5, 0)
except:
    print("PASSED")
