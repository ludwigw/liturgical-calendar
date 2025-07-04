import logging
import sys
from liturgical_calendar.config.settings import Settings

_LOGGER = None

def setup_logging(level=None, log_file=None, log_format=None):
    """
    Set up project-wide logging. Call this at the start of any script or CLI entry point.
    Args:
        level: Log level (str or int), e.g. 'INFO', 'DEBUG'.
        log_file: Optional file path to log to a file instead of stderr.
        log_format: Optional log format string.
    """
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER
    if level is None:
        level = getattr(Settings, 'LOG_LEVEL', 'INFO')
    if log_file is None:
        log_file = getattr(Settings, 'LOG_FILE', None)
    if log_format is None:
        log_format = getattr(Settings, 'LOG_FORMAT', '%(asctime)s %(levelname)s [%(name)s] %(message)s')
    handlers = []
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    else:
        handlers.append(logging.StreamHandler(sys.stderr))
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    _LOGGER = logging.getLogger('liturgical_calendar')
    return _LOGGER

def get_logger(name=None):
    """
    Get a logger for a specific module or use the project-wide logger.
    """
    if _LOGGER is None:
        setup_logging()
    return logging.getLogger(name or 'liturgical_calendar') 