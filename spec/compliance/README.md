# Compliance Suite

This folder contains schema validation and golden manifests.

- `validate_manifest.py` validates a **Bundle Directory** (containing `manifest.json`, `context.log`, etc.) against the Schema and File Layout.
- `golden/valid_bundle/` is a known-good reference bundle that passes all strict checks.

Usage:
python spec/compliance/validate_manifest.py spec/compliance/golden/valid_bundle/manifest.json
