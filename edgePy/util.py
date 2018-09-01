""" Utilities to support functions and classes """
import logzero  # type: ignore


def _setup_log():
    """Formats and sets up the logger instance.

    Returns:
        An instance of a logger.
    """
    _log_format = (
        "%(color)s[%(levelname)s] [%(asctime)s | "
        "%(module)s - line %(lineno)d]:%(end_color)s %(message)s"
    )
    _formatter = logzero.LogFormatter(fmt=_log_format)

    logger = logzero.setup_logger(logfile=None, level=logzero.logging.INFO, formatter=_formatter)

    return logger


# Logger instance constant
LOG = _setup_log()
