"""Tests for validate_manifest.py — the compliance gatekeeper."""

import json
import sys
from pathlib import Path

# Add parent directory to sys.path so we can import validate_manifest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validate_manifest import check_filesystem, load_schema, validate_file  # noqa: E402

GOLDEN_DIR = Path(__file__).resolve().parent.parent / "golden"


# ---------------------------------------------------------------------------
# load_schema
# ---------------------------------------------------------------------------
class TestLoadSchema:
    def test_returns_dict_with_schema_key(self):
        schema = load_schema()
        assert isinstance(schema, dict)
        assert "$schema" in schema

    def test_schema_has_required_top_level_properties(self):
        schema = load_schema()
        required = schema.get("required", [])
        for field in ("schemaVersion", "meta", "context", "steps", "exception", "artifacts"):
            assert field in required, f"Missing required field: {field}"


# ---------------------------------------------------------------------------
# Golden valid bundle — must pass
# ---------------------------------------------------------------------------
class TestValidBundle:
    def test_valid_bundle_passes(self, validator):
        manifest_path = GOLDEN_DIR / "9f2a0c1b3d4e5a6b_20260202T143000Z" / "manifest.json"
        assert manifest_path.exists(), f"Golden valid bundle missing: {manifest_path}"
        result = validate_file(manifest_path, validator)
        assert result is True


# ---------------------------------------------------------------------------
# Golden invalid bundles — must fail
# ---------------------------------------------------------------------------
class TestInvalidMissingManifest:
    def test_missing_manifest_fails(self, validator):
        """Bundle directory exists but has no manifest.json."""
        manifest_path = GOLDEN_DIR / "invalid_missing_manifest" / "manifest.json"
        # validate_file should detect that the file doesn't exist
        result = validate_file(manifest_path, validator)
        assert result is False


class TestInvalidMissingContext:
    def test_missing_context_log_fails(self, validator):
        """Manifest declares context.log but the file is absent."""
        manifest_path = GOLDEN_DIR / "invalid_missing_context" / "manifest.json"
        assert manifest_path.exists(), "Test fixture missing"
        result = validate_file(manifest_path, validator)
        assert result is False


class TestInvalidExtraFile:
    def test_extra_file_in_bundle_fails(self, validator):
        """Bundle contains rogue.txt not declared in manifest."""
        manifest_path = GOLDEN_DIR / "invalid_extra_file" / "manifest.json"
        assert manifest_path.exists(), "Test fixture missing"
        result = validate_file(manifest_path, validator)
        assert result is False


class TestInvalidPathTraversal:
    def test_path_traversal_fails(self, validator):
        """Manifest artifact value contains '../../../etc/passwd'."""
        manifest_path = GOLDEN_DIR / "invalid_path_traversal" / "manifest.json"
        assert manifest_path.exists(), "Test fixture missing"
        result = validate_file(manifest_path, validator)
        assert result is False


class TestInvalidAttachmentsUndeclared:
    def test_undeclared_attachments_dir_fails(self, validator):
        """attachments/ directory exists on disk but not declared in manifest."""
        manifest_path = GOLDEN_DIR / "invalid_attachments_undeclared" / "manifest.json"
        assert manifest_path.exists(), "Test fixture missing"
        result = validate_file(manifest_path, validator)
        assert result is False


# ---------------------------------------------------------------------------
# check_filesystem — unit tests with tmp_path fixtures
# ---------------------------------------------------------------------------
class TestCheckFilesystemUnit:
    @staticmethod
    def _make_bundle(tmp_path, manifest_dict, extra_files=None, extra_dirs=None):
        """Create a minimal bundle in tmp_path and return the manifest Path."""
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_dict), encoding="utf-8")
        # Create context.log (always expected)
        (tmp_path / "context.log").write_text("BlackBox context log\n", encoding="utf-8")
        if extra_files:
            for name, content in extra_files.items():
                (tmp_path / name).write_text(content, encoding="utf-8")
        if extra_dirs:
            for dirname in extra_dirs:
                (tmp_path / dirname).mkdir(parents=True, exist_ok=True)
        return manifest_path

    @staticmethod
    def _minimal_manifest(bundle_dir_name="test_bundle", **artifact_overrides):
        """Return a valid manifest dict with optional artifact overrides."""
        artifacts = {"bundleDir": bundle_dir_name, "logs": "context.log"}
        artifacts.update(artifact_overrides)
        return {
            "schemaVersion": 1,
            "meta": {
                "testId": "abcdef0123456789",
                "testName": "test",
                "testClass": "test.py",
                "status": "FAILED",
                "timestamp": "2026-01-01T00:00:00Z",
                "durationMs": 0,
                "runId": "00000000-0000-0000-0000-000000000000",
                "framework": {"name": "pytest", "version": "8.0.0"},
                "runtime": {"language": "python", "version": "3.11.0", "os": "Linux"},
            },
            "context": {},
            "steps": [],
            "exception": {"type": "AssertionError", "message": "fail"},
            "artifacts": artifacts,
        }

    def test_clean_bundle_passes(self, tmp_path):
        manifest = self._minimal_manifest(bundle_dir_name=tmp_path.name)
        path = self._make_bundle(tmp_path, manifest)
        assert check_filesystem(path, manifest) is True

    def test_absolute_linux_path_rejected(self, tmp_path):
        manifest = self._minimal_manifest(logs="/etc/passwd")
        path = self._make_bundle(tmp_path, manifest)
        assert check_filesystem(path, manifest) is False

    def test_windows_drive_letter_rejected(self, tmp_path):
        manifest = self._minimal_manifest(logs="C:\\Windows\\System32\\config.log")
        path = self._make_bundle(tmp_path, manifest)
        assert check_filesystem(path, manifest) is False

    def test_unc_path_rejected(self, tmp_path):
        manifest = self._minimal_manifest(logs="\\\\server\\share\\file.log")
        path = self._make_bundle(tmp_path, manifest)
        assert check_filesystem(path, manifest) is False

    def test_declared_attachments_dir_must_exist(self, tmp_path):
        manifest = self._minimal_manifest(attachmentsDir="attachments/")
        path = self._make_bundle(tmp_path, manifest)
        # attachments/ dir not created → should fail
        assert check_filesystem(path, manifest) is False

    def test_declared_attachments_dir_exists_passes(self, tmp_path):
        manifest = self._minimal_manifest(
            bundle_dir_name=tmp_path.name, attachmentsDir="attachments/"
        )
        path = self._make_bundle(tmp_path, manifest, extra_dirs=["attachments"])
        # Put a file inside so it's not empty but still acceptable
        (tmp_path / "attachments" / "file.txt").write_text("data", encoding="utf-8")
        assert check_filesystem(path, manifest) is True


# ---------------------------------------------------------------------------
# Schema validation — missing required fields
# ---------------------------------------------------------------------------
class TestSchemaValidation:
    def test_missing_exception_field_fails(self, validator, tmp_path):
        """Manifest missing the required 'exception' field."""
        manifest_data = {
            "schemaVersion": 1,
            "meta": {
                "testId": "abcdef0123456789",
                "testName": "test",
                "testClass": "test.py",
                "status": "FAILED",
                "timestamp": "2026-01-01T00:00:00Z",
                "durationMs": 0,
                "runId": "00000000-0000-0000-0000-000000000000",
                "framework": {"name": "pytest", "version": "8.0.0"},
                "runtime": {"language": "python", "version": "3.11.0", "os": "Linux"},
            },
            "context": {},
            "steps": [],
            # "exception" intentionally missing
            "artifacts": {"bundleDir": "test", "logs": "context.log"},
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")
        (tmp_path / "context.log").write_text("log\n", encoding="utf-8")
        result = validate_file(manifest_path, validator)
        assert result is False

    def test_wrong_schema_version_fails(self, validator, tmp_path):
        """schemaVersion is 99 instead of 1."""
        manifest_data = {
            "schemaVersion": 99,
            "meta": {
                "testId": "abcdef0123456789",
                "testName": "test",
                "testClass": "test.py",
                "status": "FAILED",
                "timestamp": "2026-01-01T00:00:00Z",
                "durationMs": 0,
                "runId": "00000000-0000-0000-0000-000000000000",
                "framework": {"name": "pytest", "version": "8.0.0"},
                "runtime": {"language": "python", "version": "3.11.0", "os": "Linux"},
            },
            "context": {},
            "steps": [],
            "exception": {"type": "Error", "message": "fail"},
            "artifacts": {"bundleDir": "test", "logs": "context.log"},
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")
        (tmp_path / "context.log").write_text("log\n", encoding="utf-8")
        result = validate_file(manifest_path, validator)
        assert result is False

    def test_invalid_test_id_pattern_fails(self, validator, tmp_path):
        """testId contains uppercase letters, violating ^[0-9a-f]{8,32}$."""
        manifest_data = {
            "schemaVersion": 1,
            "meta": {
                "testId": "INVALID_HEX_ID!",
                "testName": "test",
                "testClass": "test.py",
                "status": "FAILED",
                "timestamp": "2026-01-01T00:00:00Z",
                "durationMs": 0,
                "runId": "00000000-0000-0000-0000-000000000000",
                "framework": {"name": "pytest", "version": "8.0.0"},
                "runtime": {"language": "python", "version": "3.11.0", "os": "Linux"},
            },
            "context": {},
            "steps": [],
            "exception": {"type": "Error", "message": "fail"},
            "artifacts": {"bundleDir": "test", "logs": "context.log"},
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")
        (tmp_path / "context.log").write_text("log\n", encoding="utf-8")
        result = validate_file(manifest_path, validator)
        assert result is False
