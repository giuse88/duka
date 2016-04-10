import sys
import os
import argparse
import logging
import signal
from datetime import datetime

TEMPLATE = '%(asctime)s - %(levelname)s - %(threadName)s [%(thread)d] -  %(message)s'


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def is_debug_mode():
    log_env = os.getenv('LOG', None)
    if log_env is not None:
        return log_env.upper() == 'DEBUG'
    else:
        return False


def get_logger():
    logger = logging.getLogger('duka')
    if is_debug_mode():
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter(TEMPLATE))
        out_hdlr.setLevel(logging.INFO)
        logger.addHandler(out_hdlr)
        logger.setLevel(logging.INFO)
    return logger


Logger = get_logger()


def set_up_signals():
    def signal_handler(signal, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
