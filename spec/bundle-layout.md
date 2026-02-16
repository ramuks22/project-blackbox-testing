# BlackBox Bundle Layout

This document defines the filesystem contract for a BlackBox crash bundle.

## Output root

Default output directory name: `blackbox-reports/` under the adapter project directory (or project root). Must be configurable:

- Java: `-Dblackbox.outputDir=...`
- Python: env var `BLACKBOX_OUTPUT_DIR`
- Node: env var `BLACKBOX_OUTPUT_DIR`

## Bundle directory naming (MUST)

Each failure produces exactly one bundle directory named:
`{testId}_{timestamp}`

- `testId`: lowercase hex 8-32 chars
- `timestamp`: UTC in `YYYYMMDDTHHMMSSZ`

Example:
`blackbox-reports/9f2a0c1b3d4e5a6b_20260202T143000Z/`

## Required files on failure

- `manifest.json` (required)
- `context.log` (required)

## Optional directories

- `artifacts/` for tool-generated artifacts with standardized names
- `attachments/` for user-provided attachments

## Standard artifact filenames (if present)

- `artifacts/trace.zip`
- `artifacts/screenshot.png`
- `artifacts/console.txt`
- `artifacts/network.har`

## Rules

- Create bundles only on failure (no noise on pass).
- `manifest.json` `meta.status` must be "FAILED".
- `manifest.json` must only use relative paths (no absolute paths).
- `context.log` is a human-readable narrative of steps + key context values. Its format is intentionally unstructured and MUST NOT be relied upon for machine parsing. Cross-adapter variation in formatting is expected and acceptable.
- `manifest.json` `meta.runId` must be identical across all bundles produced in a single test-runner invocation (process). This enables cross-failure correlation within a run.
- Adapters must never invent extra top-level files in the bundle root beyond the spec.
