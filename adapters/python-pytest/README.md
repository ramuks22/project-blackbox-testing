# BlackBox Pytest Adapter

## Prerequisites

- Python 3.8+
- pytest 7+

## Install

```bash
cd adapters/python-pytest
python3 -m pip install -e .
```

## Usage

```python
def test_fails(blackbox):
    blackbox.log("user", "alice")
    blackbox.step("start")
    blackbox.attach("note.txt", "hello")
    assert 1 == 2
```

Optional autouse mode:

- `pytest.ini`: `blackbox_autouse = true`
- CLI: `--blackbox-autouse`

## Running tests

Run unit tests (must pass):

```bash
cd adapters/python-pytest
python3 -m pytest -q tests/test_plugin_units.py
```

Run the demo failing test (expected failure, emits bundle):

```bash
cd adapters/python-pytest
python3 -m pytest -q tests/test_failing.py
```

## TestId derivation

`canonical = "{testClass}::{testName}"`

- `testClass`: nodeid file component (module path)
- `testName`: function name without parameter IDs
- `testId`: `sha1(canonical).hexdigest().slice(0, 16)`

## Output directory

Default: `blackbox-reports/`

Override: env var `BLACKBOX_OUTPUT_DIR`
