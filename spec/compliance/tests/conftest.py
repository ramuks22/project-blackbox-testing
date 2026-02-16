import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_PATH = Path(__file__).resolve().parents[1] / ".." / "manifest.schema.json"


@pytest.fixture(scope="session")
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def validator(schema):
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
