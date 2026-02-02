from __future__ import annotations

import hashlib
import json
import os
import platform
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest

LEVELS = {"DEBUG", "INFO", "WARN", "ERROR"}
STASH_KEY = object()
RUN_ID = str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_ts(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def bundle_ts(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def sha1_16(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def to_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [to_json_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_json_value(v) for k, v in value.items()}
    return str(value)


def sanitize_filename(name: str) -> str:
    if not name:
        return "attachment"
    safe = "".join(c if c.isalnum() or c in ".-_" else "_" for c in name)
    return safe or "attachment"


def autouse_enabled(config) -> bool:
    if config.getoption("blackbox_autouse"):
        return True
    value = str(config.getini("blackbox_autouse")).strip().lower()
    return value in {"1", "true", "yes", "on"}


@dataclass
class State:
    test_class: str
    test_name: str
    test_id: str
    start_time: datetime
    run_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[Tuple[str, str]] = field(default_factory=list)
    parameters: Optional[Dict[str, Any]] = None


class BlackBoxRecorder:
    def __init__(self, state: State) -> None:
        self._state = state

    def log(self, key: str, value: Any) -> None:
        self._state.context[key] = to_json_value(value)

    def step(self, message: str, level: str = "INFO", data: Any = None) -> None:
        level_norm = level.upper() if level else "INFO"
        if level_norm not in LEVELS:
            level_norm = "INFO"
        entry: Dict[str, Any] = {
            "ts": iso_ts(utc_now()),
            "level": level_norm,
            "message": message,
        }
        if data is not None:
            entry["data"] = to_json_value(data)
        self._state.steps.append(entry)

    def attach(self, name: str, content: str) -> None:
        self._state.attachments.append((sanitize_filename(name), content or ""))


def create_state(item) -> State:
    nodeid = item.nodeid
    test_class = nodeid.split("::")[0]
    name = getattr(item, "originalname", None) or item.name
    if "[" in name:
        name = name.split("[", 1)[0]
    test_name = name
    canonical = f"{test_class}::{test_name}"
    test_id = sha1_16(canonical)

    parameters = None
    if hasattr(item, "callspec"):
        params = {k: to_json_value(v) for k, v in item.callspec.params.items()}
        if params:
            parameters = params

    return State(
        test_class=test_class,
        test_name=test_name,
        test_id=test_id,
        start_time=utc_now(),
        run_id=RUN_ID,
        parameters=parameters,
    )


def get_state(item) -> State:
    stash = getattr(item, "stash", None)
    if stash is not None:
        if STASH_KEY not in stash:
            stash[STASH_KEY] = create_state(item)
        return stash[STASH_KEY]
    if not hasattr(item, "_blackbox_state"):
        item._blackbox_state = create_state(item)
    return item._blackbox_state


def output_dir() -> str:
    return os.environ.get("BLACKBOX_OUTPUT_DIR", "blackbox-reports")


def write_context_log(state: State, path: Path, end_time: datetime, duration_ms: int) -> None:
    lines = []
    lines.append("BlackBox context log")
    lines.append(f"testClass={state.test_class}")
    lines.append(f"testName={state.test_name}")
    lines.append(f"testId={state.test_id}")
    lines.append(f"runId={state.run_id}")
    lines.append("status=FAILED")
    lines.append(f"timestamp={iso_ts(end_time)}")
    lines.append(f"durationMs={duration_ms}")
    lines.append("")
    lines.append("context:")
    if not state.context:
        lines.append("- (none)")
    else:
        for k, v in state.context.items():
            lines.append(f"- {k}: {json.dumps(v)}")
    lines.append("")
    lines.append("steps:")
    if not state.steps:
        lines.append("- (none)")
    else:
        for s in state.steps:
            data = s.get("data")
            extra = f" | data={json.dumps(data)}" if data is not None else ""
            lines.append(f"- [{s['ts']}] {s['level']} {s['message']}{extra}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_bundle(state: State, excinfo, report) -> None:
    end_time = utc_now()
    duration_ms = int((end_time - state.start_time).total_seconds() * 1000)

    out = output_dir()
    out_path = Path(out)
    if not out_path.is_absolute():
        out_path = Path.cwd() / out_path

    bundle_name = f"{state.test_id}_{bundle_ts(end_time)}"
    bundle_dir = out_path / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=True)

    attachments_created = False
    if state.attachments:
        attachments_dir = bundle_dir / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)
        attachments_created = True
        name_counts: Dict[str, int] = {}
        for name, content in state.attachments:
            count = name_counts.get(name, 0)
            name_counts[name] = count + 1
            final_name = name if count == 0 else f"{name}-{count}"
            (attachments_dir / final_name).write_text(content, encoding="utf-8")

    write_context_log(state, bundle_dir / "context.log", end_time, duration_ms)

    exc_type = excinfo.type.__name__ if excinfo else "Exception"
    exc_message = str(excinfo.value) if excinfo else "Test failed"
    exc_stack = report.longreprtext if hasattr(report, "longreprtext") else None

    exception: Dict[str, Any] = {
        "type": exc_type,
        "message": exc_message,
    }
    if exc_stack:
        exception["stackTrace"] = exc_stack

    manifest: Dict[str, Any] = {
        "schemaVersion": 1,
        "meta": {
            "testId": state.test_id,
            "testName": state.test_name,
            "testClass": state.test_class,
            "status": "FAILED",
            "timestamp": iso_ts(end_time),
            "durationMs": duration_ms,
            "runId": state.run_id,
            "framework": {"name": "pytest", "version": pytest.__version__},
            "runtime": {
                "language": "python",
                "version": platform.python_version(),
                "os": platform.system(),
                "arch": platform.machine(),
            },
        },
        "context": state.context,
        "steps": state.steps,
        "exception": exception,
        "artifacts": {
            "bundleDir": bundle_name,
            "logs": "context.log",
        },
    }

    if state.parameters:
        manifest["meta"]["parameters"] = state.parameters

    if (bundle_dir / "attachments").exists():
        manifest["artifacts"]["attachmentsDir"] = "attachments/"

    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def pytest_addoption(parser) -> None:
    parser.addini("blackbox_autouse", "Enable blackbox autouse fixture", default="false")
    group = parser.getgroup("blackbox")
    group.addoption(
        "--blackbox-autouse",
        action="store_true",
        help="Enable BlackBox autouse fixture",
    )


@pytest.fixture
def blackbox(request):
    state = get_state(request.node)
    return BlackBoxRecorder(state)


@pytest.fixture(autouse=True)
def _blackbox_autouse(request):
    if autouse_enabled(request.config):
        state = get_state(request.node)
        request.node.blackbox = BlackBoxRecorder(state)
    yield


def pytest_runtest_setup(item):
    state = get_state(item)
    state.start_time = utc_now()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        state = get_state(item)
        write_bundle(state, call.excinfo, report)
