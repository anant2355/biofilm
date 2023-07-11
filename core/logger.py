import logging
import logging.handlers
import os
import re
import inspect
import datetime
from logging.handlers import TimedRotatingFileHandler


LOG_LEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(inspect.stack()[-1].filename)), 'logs/log.log') 

loggers = {}

def get_logger(name):
    #creating more than one logger/handler instance for a name will create duplicate messages
    #if a handler exists for a name - return that instance

    if loggers.get(name):
        return loggers.get(name)

    #create one if not present and record it in the loggers
    logger = logging.getLogger(name)
    logger.propagate = False

    logger.setLevel(logging.INFO)
    logging.getLogger().setLevel(logging.WARN)  # root logger is WARN
    stream_handler = logging.StreamHandler()
    #create a formatter that removes new-line characters and add it to the console handler
    formatter = OneLineExceptionFormatter('%(asctime)s %(threadName)s %(name)s %(levelname)s %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    if LOG_FILE:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter('%(asctime)s %(threadName)s %(name)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(LOG_LEVEL)
    loggers[name] = logger

    return logger

class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record):
        result = super().format(record)
        result = result.replace("\n", " ")
        return result
