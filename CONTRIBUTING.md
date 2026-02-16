# Contributing to BlackBox Testing

Thank you for contributing to the BlackBox Crash Bundle Standard.

## Developer Certificate of Origin (DCO)

All contributions must be accompanied by a Developer Certificate of Origin (DCO).
Include the following line in each commit message:

```text
Signed-off-by: Random J Developer <random@developer.example.org>
```

Git can add this automatically:

```bash
git commit -s -m "feat: my new feature"
```

## Pull request process

1. Strict compliance: adapter and tooling changes must pass `make compliance`.
2. Spec-first: contract changes must be defined in `spec/` before implementation.
3. Schema-first for contract edits: if behavior changes the manifest/layout, update `spec/manifest.schema.json` and docs first.

## Development environment

Use the Makefile entry points:

- `make install`: install dependencies for all adapters and tools.
- `make lint`: run lint gates (`ruff`, `black --check`, `eslint`, `shellcheck`).
- `make test-units`: run validator and adapter unit tests.
- `make compliance`: run the full compliance suite (includes unit tests).
- `make test`: run failing demo tests to generate sample bundles.
- `make clean`: remove generated artifacts and bundles.

## Submitting a pull request

1. Fork the repository and create a branch from `main`.
2. Keep branches focused on a single change (spec-only, adapter-only, or tooling-only whenever possible).
3. Run local quality gates from the repository root:
   - `make lint`
   - `make test-units`
   - `make compliance`
4. Ensure commit messages are DCO-signed (`git commit -s ...`).
5. Open a PR against `main`; include a concise summary and validation output.

## Code style

- Python: follow PEP8/Black/Ruff.
- TypeScript: follow ESLint rules in the adapter config.
- Java: follow standard Maven/JUnit conventions.
