# Contributing to BlackBox Testing

Thank you for your interest in contributing to the BlackBox Crash Bundle Standard.

## Developer Certificate of Origin (DCO)

All contributions to this project must be accompanied by a Developer Certificate of Origin (DCO). This is a declaration that you have the right to submit the code you are contributing.

To sign off on your specific contribution, include the following line in your commit message:

    Signed-off-by: Random J Developer <random@developer.example.org>

Git has a `-s` flag to `git commit` that automates this:

    git commit -s -m "feat: my new feature"

## Pull Request Process

1.  **Strict Compliance**: Any changes to adapters MUST pass the compliance suite (`make compliance`).
2.  **Spec-First**: Changes to the bundle layout or manifest contract must be defined in `spec/` before implementation.
3.  **One Bundle**: Identify if your change impacts the schema. If so, update `manifest.schema.json` first.

## Development Environment

Use the provided Makefile to orchestrate the repo:

-   `make install`: Install dependencies
-   `make lint`: Run lint gates (ruff/black, eslint, shellcheck)
-   `make compliance`: Run the compliance suite against all adapters

## Code Style

-   **Python**: Follow PEP8 / Black.
-   **TypeScript**: Follow standard linting rules provided.
-   **Java**: Standard Maven conventions.
