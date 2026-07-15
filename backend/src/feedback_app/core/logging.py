"""Logging configuration.

Two small, single-purpose helpers: one to configure the root logger once,
one to hand out named loggers to modules.
"""
import logging
import sys

_CONFIGURED = False
_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configure_logging(level: str = "DEBUG") -> None:
    """Configure the root logger exactly once.

    Levels used across the app: DEBUG (fine-grained flow), INFO (notable
    actions), WARNING (expected-but-abnormal, e.g. bad credentials),
    ERROR/EXCEPTION (unexpected failures).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_FORMAT))

    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers.clear()
    root.addHandler(handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""
    return logging.getLogger(name)
