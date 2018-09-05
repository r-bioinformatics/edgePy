""" Utilities to support functions and classes """
from typing import Optional

import logzero  # type: ignore

__all__ = ["getLogger"]

LOG_FORMAT = (
    "%(color)s[%(levelname)s | %(asctime)s | "
    "%(name)s | %(module)s | line %(lineno)d]:%(end_color)s %(message)s"
)


def getLogger(
    name: str,
    level: int = logzero.logging.DEBUG,
    formatter: Optional[logzero.LogFormatter] = logzero.LogFormatter(fmt=LOG_FORMAT),
) -> logzero.logger:
    """Formats and sets up the logger instance.

    Args:
        name (str): The name of the Logger.
        level (int): The default level (logzero.logging.INFO = 20) of the logger.
        formatter (:obj:, optional): The format of the log message. Defaults to the default logzero format.

    Returns:
        An instance of a logger.

    Examples:
        >>> from edgePy.util import getLogger
        >>> log = getLogger(name="script")
        >>> log.info('This is your DGElist.')
        ...

    Notes:
        1. See https://docs.python.org/3/library/logging.html#levels for more information about logging levels.

    """
    log_formatter = (
        logzero.LogFormatter(fmt=logzero.LogFormatter.DEFAULT_FORMAT)
        if formatter is None
        else formatter
    )
    logger = logzero.setup_logger(name=name, level=level, formatter=log_formatter)

    return logger
