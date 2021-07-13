import logging
logging.basicConfig(format='%(asctime)s  %(levelname)s : %(message)s')

from .base import BaseLogger

class Logger(BaseLogger):

    @staticmethod
    def info(msg):
        logging.getLogger().setLevel(logging.INFO)
        logging.info(msg)

    @staticmethod
    def error(msg):
        logging.error(msg)

    @staticmethod
    def exception(msg):
        logging.exception(msg)

    @staticmethod
    def warn(msg):
        logging.warn(msg)