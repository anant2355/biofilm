import time
import functools
from datetime import timedelta
from core.logger import get_logger

logger = get_logger('perf')


class Metric:
    @staticmethod
    def log_it(hint: str, elapsed_time=None):
        if elapsed_time is None:
            logger.info('{}'.format(hint))
        else:
            logger.info('In elapsed_time={}, {}'.format(elapsed_time, hint), extra={'elapsed_time': elapsed_time})


def time_it(name, log_input=False, log_output=False):
    """
    Meter time for execution of the method
    Usage:

    @time_it('ocr')
    def my_method(args1,args2):
        ... ....

    :param name:
    :param log_output: whether to log the result
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            start_time = time.time()
            if log_input:
                Metric.log_it('Starting {} with input={}'.format(name, args))
            else:
                Metric.log_it('Starting {}'.format(name))
            ret = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = timedelta(seconds=(end_time - start_time))
            if log_output:
                Metric.log_it('Done {} with input={} and output={}'.format(name, args, ret), elapsed_time)
            else:
                Metric.log_it('Done {} '.format(name), elapsed_time)
            return ret

        return wrapper_timer

    return decorator
