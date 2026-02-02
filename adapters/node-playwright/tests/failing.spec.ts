import { test, expect } from "../src/fixtures";

test("blackbox records failure", async ({ blackbox }) => {
  blackbox.log("user", "alice");
  blackbox.step("start");
  blackbox.attach("note.txt", "hello");
  expect(1).toBe(2);
});
