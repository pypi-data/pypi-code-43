from ubcs_auxiliary import threading

def test_start_new_thread():
    def func(*args,**kwargs):
        global sum_value
        global kwargs_list
        from numpy import sum
        sum_value = sum(args)
        kwargs_list = list(kwargs.keys())

    from time import sleep
    global sum_value
    global kwargs_list
    sum_value = None
    kwargs_list = None
    thread = threading.start_new_safe_thread(func,1,2,3,4,5,6 , daemon = True, keyword1 = '', keyword2 = 5)
    while kwargs_list is None:
        sleep(0.01)
    assert sum_value == 21
    assert kwargs_list == ['keyword1','keyword2']

def test_start_new_thread2():
    from time import sleep
    global sum_value
    global kwargs_list
    def func(*args,**kwargs):
        global sum_value
        global kwargs_list
        from numpy import sum
        sum_value = sum(args)
        kwargs_list = list(kwargs.keys())
    sum_value = None
    kwargs_list = None
    threading.start_new_safe_thread(func,-1,-2,-3,-4,-5,-6, keyword12 = '', keyword22 = 5)
    while kwargs_list is None:
        sleep(0.01)
    assert sum_value == -21
    assert kwargs_list == ['keyword12','keyword22']
