import { test as base, expect } from "@playwright/test";
import { BlackBoxRecorder } from "./blackbox";

type Fixtures = {
  blackbox: BlackBoxRecorder;
};

export const test = base.extend<Fixtures>({
  blackbox: async ({}, use, testInfo) => {
    const recorder = new BlackBoxRecorder(testInfo);
    await use(recorder);
    await recorder.maybeWriteBundle(testInfo);
  },
});

export { expect };
