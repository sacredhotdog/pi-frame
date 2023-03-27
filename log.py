import logging
import os


_LOG_FILE = os.getenv("PI_FRAME_LOG_FILE")
_LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def info(log_message):
    logging.info(log_message)


def warn(log_message):
    logging.warning(log_message)


def error(log_message):
    logging.error(log_message)


logging.basicConfig(level=logging.INFO, filename=_LOG_FILE, format=_LOG_FORMAT)
