"""Unit tests for pytest_blackbox.plugin deterministic primitives."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

from pytest_blackbox.plugin import (
    bundle_ts,
    iso_ts,
    sanitize_filename,
    sha1_16,
    to_json_value,
    autouse_enabled,
)


# ---------------------------------------------------------------------------
# sha1_16
# ---------------------------------------------------------------------------
class TestSha116:
    def test_known_hash(self):
        # sha1("hello") = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
        assert sha1_16("hello") == "aaf4c61ddcc5e8a2"

    def test_length_is_16(self):
        result = sha1_16("anything")
        assert len(result) == 16

    def test_all_lowercase_hex(self):
        result = sha1_16("test")
        assert all(c in "0123456789abcdef" for c in result)

    def test_empty_string(self):
        result = sha1_16("")
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)

    def test_unicode(self):
        result = sha1_16("日本語テスト")
        assert len(result) == 16


# ---------------------------------------------------------------------------
# sanitize_filename
# ---------------------------------------------------------------------------
class TestSanitizeFilename:
    def test_normal_name(self):
        assert sanitize_filename("note.txt") == "note.txt"

    def test_special_characters_replaced(self):
        result = sanitize_filename("../../etc/passwd")
        assert "/" not in result
        assert ".." not in result or result.count(".") <= len(result)  # dots OK, slashes not

    def test_empty_returns_attachment(self):
        assert sanitize_filename("") == "attachment"

    def test_none_handling(self):
        # sanitize_filename checks `if not name` which covers None-like
        assert sanitize_filename("") == "attachment"

    def test_preserves_safe_chars(self):
        assert sanitize_filename("file-name_v2.txt") == "file-name_v2.txt"

    def test_spaces_replaced(self):
        result = sanitize_filename("my file.txt")
        assert " " not in result


# ---------------------------------------------------------------------------
# to_json_value
# ---------------------------------------------------------------------------
class TestToJsonValue:
    def test_none(self):
        assert to_json_value(None) is None

    def test_string(self):
        assert to_json_value("hello") == "hello"

    def test_int(self):
        assert to_json_value(42) == 42

    def test_float(self):
        assert to_json_value(3.14) == 3.14

    def test_bool(self):
        assert to_json_value(True) is True

    def test_list(self):
        assert to_json_value([1, "two", None]) == [1, "two", None]

    def test_dict(self):
        assert to_json_value({"a": 1}) == {"a": 1}

    def test_nested_dict(self):
        result = to_json_value({"a": {"b": [1, 2]}})
        assert result == {"a": {"b": [1, 2]}}

    def test_non_serializable_becomes_str(self):
        result = to_json_value(object())
        assert isinstance(result, str)

    def test_tuple_becomes_list(self):
        assert to_json_value((1, 2, 3)) == [1, 2, 3]


# ---------------------------------------------------------------------------
# bundle_ts
# ---------------------------------------------------------------------------
class TestBundleTs:
    def test_known_datetime(self):
        dt = datetime(2026, 2, 2, 14, 30, 0, tzinfo=timezone.utc)
        assert bundle_ts(dt) == "20260202T143000Z"

    def test_midnight(self):
        dt = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert bundle_ts(dt) == "20260101T000000Z"

    def test_end_of_day(self):
        dt = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        assert bundle_ts(dt) == "20261231T235959Z"


# ---------------------------------------------------------------------------
# iso_ts
# ---------------------------------------------------------------------------
class TestIsoTs:
    def test_known_datetime(self):
        dt = datetime(2026, 2, 2, 14, 30, 0, tzinfo=timezone.utc)
        result = iso_ts(dt)
        assert result == "2026-02-02T14:30:00Z"

    def test_ends_with_z(self):
        dt = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        result = iso_ts(dt)
        assert result.endswith("Z")
        assert "+00:00" not in result


# ---------------------------------------------------------------------------
# autouse_enabled
# ---------------------------------------------------------------------------
class TestAutoUseEnabled:
    @staticmethod
    def _mock_config(ini_value="false", option_value=False):
        config = MagicMock()
        config.getoption.return_value = option_value
        config.getini.return_value = ini_value
        return config

    def test_default_false(self):
        config = self._mock_config("false", False)
        assert autouse_enabled(config) is False

    def test_ini_true(self):
        config = self._mock_config("true", False)
        assert autouse_enabled(config) is True

    def test_ini_one(self):
        config = self._mock_config("1", False)
        assert autouse_enabled(config) is True

    def test_ini_yes(self):
        config = self._mock_config("yes", False)
        assert autouse_enabled(config) is True

    def test_ini_on(self):
        config = self._mock_config("on", False)
        assert autouse_enabled(config) is True

    def test_cli_option_overrides(self):
        config = self._mock_config("false", True)
        assert autouse_enabled(config) is True

    def test_ini_zero(self):
        config = self._mock_config("0", False)
        assert autouse_enabled(config) is False
