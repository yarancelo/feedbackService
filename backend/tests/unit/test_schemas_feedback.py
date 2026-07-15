"""Feedback schema validation + serialization."""
import datetime
import uuid

import pytest
from pydantic import ValidationError

from feedback_app.schemas.feedback import FeedbackCreate, FeedbackOut


def test_trims_whitespace():
    payload = FeedbackCreate(topic="  hi  ", body="  there  ")
    assert payload.topic == "hi"
    assert payload.body == "there"


def test_rejects_blank_topic():
    with pytest.raises(ValidationError):
        FeedbackCreate(topic="   ", body="ok")


def test_rejects_blank_body():
    with pytest.raises(ValidationError):
        FeedbackCreate(topic="ok", body="")


def test_out_from_attributes():
    class Row:
        id = uuid.uuid4()
        topic = "t"
        body = "b"
        created_at = datetime.datetime.now(datetime.timezone.utc)

    out = FeedbackOut.model_validate(Row())
    assert out.topic == "t"
