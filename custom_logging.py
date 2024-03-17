import logging

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s |%(name)s-%(process)d-%(pathname)s|%(lineno)s:: %(funcName)s|')


def setup_logger(name, log_file, level=logging.INFO):
    """To create as many loggers as you want"""

    # create a file handler
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    # create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.addHandler(handler)
    # logger.addHandler(console_handler)

    return logger
