import logging
import logging.handlers
import multiprocessing
import sys
import os

LOG_FILE = os.environ.get("APP_LOG_FILE", "app.log")
LOG_LEVEL = os.environ.get("APP_LOG_LEVEL", "INFO")
PROCESS_FRIENDLY_NAME = os.environ.get("PROCESS_FRIENDLY_NAME", "MainProcess")

class MultiprocessLogger:
    _queue = None
    _listener = None
    _logger = None

    @classmethod
    def setup_logging(cls, friendly_name=None):
        if cls._queue is not None:
            return  # Already set up
        cls._queue = multiprocessing.Queue(-1)
        cls._logger = logging.getLogger()
        cls._logger.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(
            f'%(asctime)s | %(levelname)s | %(processName)s | %(friendly_name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(lambda record: setattr(record, 'friendly_name', friendly_name or PROCESS_FRIENDLY_NAME) or True)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(lambda record: setattr(record, 'friendly_name', friendly_name or PROCESS_FRIENDLY_NAME) or True)

        cls._listener = logging.handlers.QueueListener(
            cls._queue, file_handler, console_handler, respect_handler_level=True)
        cls._listener.start()
        cls._logger.handlers = []
        cls._logger.addHandler(logging.handlers.QueueHandler(cls._queue))

    @classmethod
    def get_logger(cls, friendly_name=None):
        if cls._queue is None:
            cls.setup_logging(friendly_name)
        logger = logging.getLogger()
        logger.propagate = False
        return logger

    @classmethod
    def shutdown(cls):
        if cls._listener:
            cls._listener.stop()
            cls._listener = None
            cls._queue = None

# Usage:
# from app.logging_service import MultiprocessLogger
# logger = MultiprocessLogger.get_logger("Worker-1")
# logger.info("message")