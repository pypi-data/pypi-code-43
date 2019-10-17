def test1():
    assert 1 + 2 == 3

def test2():
    assert 0.1 + 0.2 == 0.3

#
# ======================================================================
# FAIL: mytests.test2
# ----------------------------------------------------------------------
# Traceback (most recent call last):
#   File "lib/python3.7/site-packages/nose/case.py", line 198, in runTest
#     self.test(*self.arg)
#   File "mytests.py", line 5, in test2
#     assert 0.1 + 0.2 == 0.3
# AssertionError
#
# ----------------------------------------------------------------------
# Ran 2 tests in 0.001s
#
# FAILED (failures=1)
#
#
#
