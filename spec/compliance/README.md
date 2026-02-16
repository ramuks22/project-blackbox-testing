# Compliance Suite

This folder contains schema validation and golden manifests.

- `validate_manifest.py` validates a **Bundle Directory** (containing `manifest.json`, `context.log`, etc.) against the Schema and File Layout.
- `golden/9f2a0c1b3d4e5a6b_20260202T143000Z/` is a known-good reference bundle that passes all strict checks.

Usage:
python spec/compliance/validate_manifest.py spec/compliance/golden/9f2a0c1b3d4e5a6b_20260202T143000Z/manifest.json
