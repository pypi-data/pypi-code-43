import logging
from .experiment import Experiment

runtime_loggers = {}


def get_runtime_logger(identity):
    global runtime_loggers
    experiment = Experiment(identity)
    logger_name = f'runtime_logger_{identity}'

    if logger_name in runtime_loggers:
        return runtime_loggers[logger_name]

    runtime_logger = logging.getLogger(logger_name)
    handler = logging.FileHandler(experiment.log_file())
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s', datefmt="%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    runtime_logger.addHandler(handler)
    runtime_logger.setLevel(logging.DEBUG)
    runtime_loggers[logger_name] = runtime_logger
    return runtime_logger
