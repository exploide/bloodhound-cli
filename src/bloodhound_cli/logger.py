import logging


def init_logger():
    """Setup the logger instance for this application."""

    l = logging.getLogger(__name__)
    l.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    l.addHandler(handler)
    return l


def set_loglevel(debug):
    """Set loglevel to either DEBUG or INFO."""

    log.setLevel(logging.DEBUG if debug else logging.INFO)


log = init_logger()
