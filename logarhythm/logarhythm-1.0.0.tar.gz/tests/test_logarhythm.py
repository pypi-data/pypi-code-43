import doctest,logarhythm
def test_build_format():
    from logarhythm import build_format, LogarhythmException
    for kw in ['time','logger_name','process_name','thread_name','level']:
        kwargs = {kw:'garbage'}
        try:
            build_format(**kwargs)
        except LogarhythmException as e:
            assert('Invalid '+kw in str(e))
        

def test_logarhythm():
    import logging
    logging_default = logging.getLogger()
    logging_module = logging.getLogger(__name__)
    assert(logging_module.name == 'tests.test_logarhythm')
    logarhythm_module = logarhythm.getLogger()
    assert(logarhythm_module.name == 'tests.test_logarhythm')
    logarhythm_root = logarhythm.root_logger
    assert(logarhythm_root.name == '')
    assert(logging_default is not logarhythm_root)
    assert(logging_default is logging_module)
    assert(logging_default is logarhythm_module._logger)
    logarhythm_module.disarm_logging_module = False
    logging_default = logging.getLogger()
    logging_module = logging.getLogger(__name__)
    assert(logging_default is logarhythm_root._logger)
    assert(logging_module is logarhythm_module._logger)

def test_profiling():
    import logarhythm
    from time import sleep

    logger = logarhythm.Logger()
    logger.level = logarhythm.INFO
    with logger.profile('test_block'):
        for x in range(50):
            sleep(0.1)




if __name__ == '__main__':
    test_logarhythm()
