# Compliance Suite

This folder contains validation tooling, golden bundles, and validator unit tests for the BlackBox contract.

## Contents

- `validate_manifest.py`: validates a bundle directory against JSON schema and filesystem rules.
- `golden/9f2a0c1b3d4e5a6b_20260202T143000Z/`: known-good bundle that must pass.
- `golden/invalid_*/`: adversarial bundles that must fail:
  - `invalid_missing_manifest/`
  - `invalid_missing_context/`
  - `invalid_extra_file/`
  - `invalid_path_traversal/`
  - `invalid_attachments_undeclared/`
- `tests/`: validator unit tests.

## Usage

Validate a bundle:

```bash
python3 spec/compliance/validate_manifest.py path/to/bundle/manifest.json
```

Run validator unit tests:

```bash
cd spec/compliance
python3 -m pytest tests/ -v
```

Run full repo compliance:

```bash
make compliance
```

Compliance execution order:

1. Validator + adapter unit tests
2. Golden valid bundle check
3. Java/Python/Node failing-demo bundle checks
