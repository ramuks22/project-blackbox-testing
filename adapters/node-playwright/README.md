# BlackBox Playwright Test Adapter

## Install

npm install

## Usage

import { test, expect } from "./src/fixtures";

test("fails", async ({ blackbox }) => {
  blackbox.log("user", "alice");
  blackbox.step("start");
  blackbox.attach("note.txt", "hello");
  expect(1).toBe(2);
});

## TestId derivation

canonical = "{testClass}::{testName}"

- testClass: spec file path (relative)
- testName: testInfo.titlePath().join("::")
- testId: sha1(canonical).hexdigest().slice(0, 16)

## Output directory

Default: `blackbox-reports/`
Override: env var `BLACKBOX_OUTPUT_DIR`
