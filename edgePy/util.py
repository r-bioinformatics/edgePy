""" Utilities to support functions and classes """

from logzero import setup_logger, LogFormatter, logging


def _setup_log():
    """Formats and sets up the logger instance.

    Returns:
        An instance of a logger.
    """
    _log_format = (
        "%(color)s[%(levelname)s] [%(asctime)s | "
        "%(module)s - line %(lineno)d]:%(end_color)s %(message)s"
    )
    _formatter = LogFormatter(fmt=_log_format)

    logger = setup_logger(logfile=None, level=logging.INFO, formatter=_formatter)

    return logger


log = _setup_log()
