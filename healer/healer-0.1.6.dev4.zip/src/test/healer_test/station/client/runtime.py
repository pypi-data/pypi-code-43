"""
Invoke tests in browser
"""

from healer_test.station.base.arkon_test import  *

from browser import document
from browser.html import DIV
from javascript import Date

report_head = document['report_head']
report_body = document['report_body']

report_head.classList = ['container-fluid']
report_head.style = {'background-color': 'beige'}

report_body.classList = ['container-fluid']

report_success = DIV('success', style={'color':'green'})
report_failure = DIV('failure', style={'color':'brown'})
report_head <= report_success
report_head <= report_failure


class count_test:
    success = 0
    failure = 0


def invoke_test(test_func):
    test_name = test_func.__name__
    record = DIV(Class='row')
    report_body <= record
    record <= DIV(test_name, Class='col-sm-3')
    print(f"{test_name}: ")
    try:
        time_start = Date.new()
        test_func()
        time_finish = Date.new()
        message = 'success'
        print(message)
        record <= DIV(message, style={'color':'green'}, Class='col-sm-3')
        count_test.success += 1
    except Exception as error:
        time_finish = Date.new()
        message = f'failure: {error}'
        print(message)
        record <= DIV(message, style={'color':'brown'}, Class='col-sm-3')
        count_test.failure += 1
    time_diff = time_finish.getTime() - time_start.getTime()
    message = f"{time_diff} ms"
    record <= DIV(message, Class='col-sm-3')
    report_success.text = f'success: {count_test.success}'
    report_failure.text = f'failure: {count_test.failure}'


globals_dict = globals().copy()

for test_name in globals_dict:
    if test_name.startswith("test_"):
        test_func = globals_dict[test_name]
        invoke_test(test_func)
