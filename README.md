# BlackBox Testing

BlackBox is a spec-first Crash Bundle Standard for test failures across Java, Python, and Node.
It solves the "Missing Evidence" CI problem: tests fail, but logs/artifacts/context are incomplete or scattered.

This repository is spec-first: the contract in `spec/` is the product, and adapters are thin recorders.

## Philosophy

- Recorder, not pilot: no browser lifecycle, retries, or test selection.
- Spec-first: the schema + filesystem layout are authoritative.
- Cross-language parity: adapters emit the same bundle shape.
- Compliance enforced: adapters must pass the compliance suite in CI.

## Bundle layout (failure only)

```text
blackbox-reports/
  {testId}_{timestamp}/
    manifest.json
    context.log
    attachments/   (optional)
    artifacts/     (optional)
```

See [bundle layout](spec/bundle-layout.md) and [manifest schema](spec/manifest.schema.json) for full contract details.

## Repository structure

```text
project-blackbox-testing/
  spec/                 # contract + compliance tooling
  adapters/             # java-junit5, python-pytest, node-playwright
  tools/scripts/        # compliance + lint orchestration
  Makefile              # local developer entry points
```

## Prerequisites

- Java (JDK) 11+
- Maven 3.8+
- Python 3.8+
- Node.js 18+
- npm 9+
- shellcheck 0.8+ (required for `make lint`)

## Quickstart

1. Clone and enter the repository:

```bash
git clone https://github.com/ramuks22/project-blackbox-testing.git
cd project-blackbox-testing
```

2. Install dependencies:

```bash
make install
```

3. Run lint gates:

```bash
make lint
```

4. Run unit tests:

```bash
make test-units
```

5. Run full compliance:

```bash
make compliance
```

`make compliance` runs unit tests -> golden bundle validation -> adapter compliance checks.

6. Run a failing demo per adapter (expected to fail and emit bundles):

```bash
# Java
cd adapters/java-junit5 && mvn -q -Dtest=SampleFailingTest test

# Python
cd adapters/python-pytest && python3 -m pytest -q tests/test_failing.py

# Node
cd adapters/node-playwright && npm test
```

## Make targets

- `make install`: install dependencies for tools and adapters.
- `make lint`: run `ruff`, `black --check`, `eslint`, and `shellcheck`.
- `make test-units`: run all validator and adapter unit tests.
- `make compliance`: run the full compliance pipeline.
- `make test`: run failing demos (intended failure path).
- `make clean`: remove generated artifacts and bundles.

## Adapter API quick reference

All adapters expose the same recorder primitives:

- `log(key, value)`: typed key/value context.
- `step(message, level="INFO", data=None)`: structured step entries.
- `attach(name, content)`: write text attachments into `attachments/`.

Bundles are created only on failure.

Adapter details:

- [Java adapter](adapters/java-junit5/README.md)
- [Python adapter](adapters/python-pytest/README.md)
- [Node adapter](adapters/node-playwright/README.md)

## Dependency policy

- Compliance tooling is pinned in `tools/requirements.txt`.
- Adapters use compatible semver ranges.
- Reproducibility is enforced with lockfiles where available (currently `package-lock.json` for Node) plus CI validation.

## Non-goals

- Not a test runner or selector.
- Not a dashboard or reporting UI.
- Not retries or flake management.
- Not browser or driver lifecycle management.

## Project docs

- [Contributing guide](CONTRIBUTING.md)
- [Versioning policy](VERSIONING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
