import { test, expect } from "@playwright/test";
import {
    sha1_16,
    sanitizeFileName,
    bundleTimestamp,
    toJsonValue,
} from "../src/blackbox";

// ---------------------------------------------------------------------------
// sha1_16
// ---------------------------------------------------------------------------
test.describe("sha1_16", () => {
    test("known hash", () => {
        // sha1("hello") = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
        expect(sha1_16("hello")).toBe("aaf4c61ddcc5e8a2");
    });

    test("length is 16", () => {
        expect(sha1_16("anything")).toHaveLength(16);
    });

    test("all lowercase hex", () => {
        const result = sha1_16("test");
        expect(result).toMatch(/^[0-9a-f]{16}$/);
    });

    test("empty string", () => {
        const result = sha1_16("");
        expect(result).toHaveLength(16);
        expect(result).toMatch(/^[0-9a-f]{16}$/);
    });

    test("unicode", () => {
        const result = sha1_16("日本語テスト");
        expect(result).toHaveLength(16);
    });
});

// ---------------------------------------------------------------------------
// sanitizeFileName
// ---------------------------------------------------------------------------
test.describe("sanitizeFileName", () => {
    test("normal name", () => {
        expect(sanitizeFileName("note.txt")).toBe("note.txt");
    });

    test("special characters replaced", () => {
        const result = sanitizeFileName("../../etc/passwd");
        expect(result).not.toContain("/");
    });

    test("empty returns attachment", () => {
        expect(sanitizeFileName("")).toBe("attachment");
    });

    test("preserves safe chars", () => {
        expect(sanitizeFileName("file-name_v2.txt")).toBe("file-name_v2.txt");
    });

    test("spaces replaced", () => {
        const result = sanitizeFileName("my file.txt");
        expect(result).not.toContain(" ");
    });
});

// ---------------------------------------------------------------------------
// bundleTimestamp
// ---------------------------------------------------------------------------
test.describe("bundleTimestamp", () => {
    test("known date", () => {
        const date = new Date("2026-02-02T14:30:00Z");
        expect(bundleTimestamp(date)).toBe("20260202T143000Z");
    });

    test("midnight", () => {
        const date = new Date("2026-01-01T00:00:00Z");
        expect(bundleTimestamp(date)).toBe("20260101T000000Z");
    });

    test("end of day", () => {
        const date = new Date("2026-12-31T23:59:59Z");
        expect(bundleTimestamp(date)).toBe("20261231T235959Z");
    });
});

// ---------------------------------------------------------------------------
// toJsonValue
// ---------------------------------------------------------------------------
test.describe("toJsonValue", () => {
    test("null", () => {
        expect(toJsonValue(null)).toBeNull();
    });

    test("undefined becomes null", () => {
        expect(toJsonValue(undefined)).toBeNull();
    });

    test("string", () => {
        expect(toJsonValue("hello")).toBe("hello");
    });

    test("number", () => {
        expect(toJsonValue(42)).toBe(42);
    });

    test("boolean", () => {
        expect(toJsonValue(true)).toBe(true);
    });

    test("array", () => {
        expect(toJsonValue([1, "two", null])).toEqual([1, "two", null]);
    });

    test("object", () => {
        expect(toJsonValue({ a: 1 })).toEqual({ a: 1 });
    });

    test("nested object", () => {
        expect(toJsonValue({ a: { b: [1, 2] } })).toEqual({ a: { b: [1, 2] } });
    });

    test("bigint becomes string", () => {
        expect(toJsonValue(BigInt(9007199254740991))).toBe("9007199254740991");
    });

    test("Date becomes ISO string", () => {
        const date = new Date("2026-01-01T00:00:00Z");
        const result = toJsonValue(date) as string;
        expect(result).toBe("2026-01-01T00:00:00.000Z");
    });

    test("Error becomes object with name, message, stack", () => {
        const err = new Error("boom");
        const result = toJsonValue(err) as Record<string, unknown>;
        expect(result).toHaveProperty("name", "Error");
        expect(result).toHaveProperty("message", "boom");
        expect(result).toHaveProperty("stack");
    });
});
