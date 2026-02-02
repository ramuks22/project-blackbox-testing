# BlackBox Testing

BlackBox is a spec-first Crash Bundle Standard for test failures. The problem it solves: "Missing Evidence" in CI -- failures happen, but the evidence is missing or scattered.

This repository is spec-first. The JSON Schema and filesystem layout define the product. Adapters are thin recorders that emit identical bundles across Java, Python, and Node.

## Philosophy

- Recorder, not pilot: no browser lifecycle, retries, or test selection.
- Spec-first: the contract (schema + layout) is the product.
- Cross-language identical output: same bundle layout and manifest across runtimes.
- Compliance enforced: adapters must pass the compliance suite.

## Bundle layout (failure only)

blackbox-reports/
  {testId}_{timestamp}/
    manifest.json
    context.log
    artifacts/ (optional)
    attachments/ (optional)

See `spec/bundle-layout.md` and `spec/manifest.schema.json` for the full contract.

## Quickstart demos

### Java (JUnit 5, Maven)
cd adapters/java-junit5
mvn -q -Dtest=SampleFailingTest test

### Python (pytest)
cd adapters/python-pytest
python -m pip install -e .
python -m pytest -q tests/test_failing.py

### Node (Playwright Test)
cd adapters/node-playwright
npm install
npm test

Each failing demo writes a bundle under `blackbox-reports/` in the adapter directory.

## Compliance suite
Make sure you have `mvn`, `python3`, and `npm` installed.

make install
make compliance


## Non-goals

- Not a test runner or selector
- Not a dashboard or reporting UI
- Not retries or flake management
- Not browser or driver lifecycle management
