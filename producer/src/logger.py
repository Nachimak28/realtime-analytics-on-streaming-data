

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(log_root, file_name, file_format, file_size, debug=False):
    """Sets up logger

    Keyword arguments:
        log_root {string}: log root
        file_name {string}: log file name and path
        file_format {string}: logging format
        file_size {int}: as defined in config (in MBs)
        debug flag {boolean}: debug
    Return:
        logger object
        log file path
    """

    _logger = logging.getLogger(file_name)
    formatter = logging.Formatter(file_format)
    log_path = os.path.join(log_root, file_name)
    handler = RotatingFileHandler(
        log_path,
        maxBytes=file_size,
        backupCount=1
    )

    # if debug:
    #     handler.setLevel(logging.DEBUG)
    # else:
    #     handler.setLevel(logging.INFO)

    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    if debug:
        _logger.root.level = logging.DEBUG
        _logger.addHandler(logging.StreamHandler())
    else:
        _logger.root.level = logging.INFO

    return _logger, log_path
