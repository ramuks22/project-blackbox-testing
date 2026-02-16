# BlackBox Playwright Test Adapter

## Prerequisites

- Node.js 18+
- npm 9+

## Install

```bash
cd adapters/node-playwright
npm install
```

## Usage

Example test file in `tests/`:

```ts
import { test, expect } from "../src/fixtures";

test("fails", async ({ blackbox }) => {
  blackbox.log("user", "alice");
  blackbox.step("start");
  blackbox.attach("note.txt", "hello");
  expect(1).toBe(2);
});
```

## Running tests

Run unit tests (must pass):

```bash
cd adapters/node-playwright
npm run test:unit
```

Run the demo failing test (expected failure, emits bundle):

```bash
cd adapters/node-playwright
npm test
```

## TestId derivation

`canonical = "{testClass}::{testName}"`

- `testClass`: spec file path (relative)
- `testName`: `testInfo.titlePath().join("::")`
- `testId`: `sha1(canonical).hexdigest().slice(0, 16)`

## Output directory

Default: `blackbox-reports/`

Override: env var `BLACKBOX_OUTPUT_DIR`
