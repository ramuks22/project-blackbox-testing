#!/usr/bin/env python3
import json
import sys
from pathlib import Path

try:
    import jsonschema
except Exception:
    print("ERROR: jsonschema is required. Install with: python -m pip install jsonschema", file=sys.stderr)
    sys.exit(2)


def load_schema() -> dict:
    schema_path = Path(__file__).resolve().parents[1] / "manifest.schema.json"
    with schema_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_targets(args):
    for arg in args:
        path = Path(arg)
        if path.is_dir():
            for m in path.rglob("manifest.json"):
                yield m
        else:
            yield path


def check_filesystem(path: Path, instance: dict) -> bool:
    """
    Enforce strict bundle layout:
    1. Verify all artifact paths in manifest exist.
    2. Verify NO extra files exist in the bundle that are not in the manifest.
    3. Verify no absolute paths, path traversal (..), or Windows drive letters in values.
    4. Attachments logic: if attachmentsDir not in manifest, NO attachments/ dir allowed (even empty).
    """
    bundle_root = path.parent
    # Collect all expected relative paths from manifest
    expected_files = {"manifest.json"}
    expected_dirs = set()

    artifacts = instance.get("artifacts", {})
    
    # Check for path safety and collect expectations
    for key, val in artifacts.items():
        # Safety checks: Traversal, Absolute Linux, Absolute Windows (drive letter)
        if ".." in val or val.startswith("/") or val.startswith("\\") or (len(val) > 1 and val[1] == ":"):
             print(f"INVALID: {path} (unsafe path in artifacts: {key}={val})", file=sys.stderr)
             return False
             
        if key == "bundleDir":
            continue
            
        if val.endswith("/"):
            expected_dirs.add(val)
        else:
            expected_files.add(val)

    # 1. Verify existence
    missing = []
    for f in expected_files:
        if not (bundle_root / f).exists():
            missing.append(f)
    
    if missing:
        print(f"INVALID: {path} (missing files declared in manifest: {missing})", file=sys.stderr)
        return False
        
    # 2. Verify no extras (Strict Mode) + Attachments Logic
    extras = []
    
    # Check specifically for undeclared 'attachments' directory existence (even if empty)
    # The 'attachmentsDir' key usually has value "attachments/"
    attachments_declared = any(d == "attachments/" for d in expected_dirs)
    
    # 1. If declared, it MUST exist (Strict Spec consistency)
    if attachments_declared and not (bundle_root / "attachments").exists():
         print(f"INVALID: {path} ('attachmentsDir' declared but 'attachments/' directory missing)", file=sys.stderr)
         return False

    # 2. If present on disk, it MUST be declared
    if (bundle_root / "attachments").exists() and not attachments_declared:
         print(f"INVALID: {path} (found 'attachments/' directory but 'attachmentsDir' not in manifest)", file=sys.stderr)
         return False

    # rglob/walk the bundle_root for FILES
    for p in bundle_root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(bundle_root).as_posix()
        
        # Check if explicitly expected
        if rel in expected_files:
            continue
            
        # Check if inside an expected directory
        # e.g. rel="attachments/foo.png", expected_dirs={"attachments/"}
        is_covered = False
        for d in expected_dirs:
            if rel.startswith(d):
                is_covered = True
                break
        if is_covered:
            continue
            
        extras.append(rel)
        
    if extras:
        print(f"INVALID: {path} (contain extra files not in manifest: {extras})", file=sys.stderr)
        return False
        
    return True

def validate_file(path: Path, validator) -> bool:
    if not path.exists():
        print(f"INVALID: {path} (not found)", file=sys.stderr)
        return False
    try:
        instance = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"INVALID: {path} (invalid JSON: {exc})", file=sys.stderr)
        return False
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        print(f"INVALID: {path}", file=sys.stderr)
        for err in errors:
            loc = "/".join(str(p) for p in err.path) or "<root>"
            print(f"  - {loc}: {err.message}", file=sys.stderr)
        return False
        
    # Schema checks passed, now check strict filesystem hygiene
    if not check_filesystem(path, instance):
        return False

    print(f"OK: {path}")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate_manifest.py <manifest.json|dir> [more paths...]", file=sys.stderr)
        return 2
    schema = load_schema()
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    ok = True
    for target in iter_targets(sys.argv[1:]):
        ok = validate_file(target, validator) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
