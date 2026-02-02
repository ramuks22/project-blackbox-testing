# BlackBox Pytest Adapter

## Install

pip install -e .

## Usage

def test_fails(blackbox):
    blackbox.log("user", "alice")
    blackbox.step("start")
    blackbox.attach("note.txt", "hello")
    assert 1 == 2

Optional autouse (in pytest.ini or CLI):
- pytest.ini: blackbox_autouse = true
- CLI: --blackbox-autouse

## TestId derivation

canonical = "{testClass}::{testName}"

- testClass: nodeid file component (module path)
- testName: function name without parameter ids
- testId: sha1(canonical).hexdigest().slice(0, 16)

## Output directory

Default: `blackbox-reports/`
Override: env var `BLACKBOX_OUTPUT_DIR`
