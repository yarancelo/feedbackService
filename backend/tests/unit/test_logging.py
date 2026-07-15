"""Logging helper tests."""
import logging

import feedback_app.core.logging as logmod
from feedback_app.core.logging import configure_logging, get_logger


def test_configure_is_idempotent():
    logmod._CONFIGURED = False
    configure_logging("DEBUG")
    snapshot = list(logging.getLogger().handlers)
    configure_logging("DEBUG")  # second call must be a no-op
    assert logging.getLogger().handlers == snapshot


def test_get_logger_returns_named_logger():
    assert get_logger("abc").name == "abc"
