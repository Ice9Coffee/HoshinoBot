'''
Provide logger object.

Any other modules in "hoshino" should use "logger" from this module to log messages.
'''

import os
import sys
import logging

_error_log_file = os.path.expanduser('~/.hoshino/error.log')

formatter = logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger('hoshino')
default_handler = logging.StreamHandler(sys.stdout)
default_handler.setFormatter(formatter)
error_handler = logging.FileHandler(_error_log_file, encoding='utf8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
logger.addHandler(default_handler)
logger.addHandler(error_handler)
