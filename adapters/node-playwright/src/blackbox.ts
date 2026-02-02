import crypto from "crypto";
import { promises as fs } from "fs";
import path from "path";
import os from "os";
import type { TestInfo } from "@playwright/test";

type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };

type StepLevel = "DEBUG" | "INFO" | "WARN" | "ERROR";

interface StepRecord {
  ts: string;
  level: StepLevel;
  message: string;
  data?: JsonValue;
}

interface Attachment {
  name: string;
  content: string;
}

const LEVELS = new Set<StepLevel>(["DEBUG", "INFO", "WARN", "ERROR"]);

function toJsonValue(value: unknown): JsonValue {
  if (value === null || value === undefined) return null;
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return value;
  }
  if (typeof value === "bigint") {
    return value.toString();
  }
  if (Array.isArray(value)) {
    return value.map(toJsonValue);
  }
  if (value instanceof Date) {
    return value.toISOString();
  }
  if (value instanceof Error) {
    return {
      name: value.name,
      message: value.message,
      stack: value.stack || null,
    };
  }
  if (typeof value === "object") {
    const out: { [key: string]: JsonValue } = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = toJsonValue(v);
    }
    return out;
  }
  return String(value);
}

function sanitizeFileName(name: string): string {
  if (!name) return "attachment";
  const safe = name.replace(/[^A-Za-z0-9._-]/g, "_");
  return safe || "attachment";
}

function bundleTimestamp(date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, "0");
  return (
    date.getUTCFullYear().toString() +
    pad(date.getUTCMonth() + 1) +
    pad(date.getUTCDate()) +
    "T" +
    pad(date.getUTCHours()) +
    pad(date.getUTCMinutes()) +
    pad(date.getUTCSeconds()) +
    "Z"
  );
}

function sha1_16(input: string): string {
  return crypto.createHash("sha1").update(input).digest("hex").slice(0, 16);
}

function getPlaywrightVersion(): string {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    return require("@playwright/test/package.json").version || "unknown";
  } catch {
    return "unknown";
  }
}

export class BlackBoxRecorder {
  private context: { [key: string]: JsonValue } = {};
  private steps: StepRecord[] = [];
  private attachments: Attachment[] = [];
  private startTime: Date = new Date();
  private runId: string = crypto.randomUUID();
  private testClass: string;
  private testName: string;
  private testId: string;

  constructor(testInfo: TestInfo) {
    const filePath = testInfo.file ? path.relative(process.cwd(), testInfo.file) : "unknown";
    this.testClass = filePath.replace(/\\/g, "/");
    let tp: string[] = [];
    try {
      if (typeof testInfo.titlePath === "function") {
        tp = testInfo.titlePath();
      } else if (Array.isArray(testInfo.titlePath)) {
        tp = testInfo.titlePath;
      }
    } catch {
      // ignore
    }

    if (!Array.isArray(tp) || tp.length === 0) {
      tp = [testInfo.title || "unknown"];
    }

    this.testName = tp.join("::");
    const canonical = `${this.testClass}::${this.testName}`;
    this.testId = sha1_16(canonical);
  }

  log(key: string, value: unknown): void {
    this.context[key] = toJsonValue(value);
  }

  step(message: string, level: StepLevel = "INFO", data?: unknown): void {
    const norm = LEVELS.has(level) ? level : "INFO";
    const entry: StepRecord = {
      ts: new Date().toISOString(),
      level: norm,
      message,
    };
    if (data !== undefined) {
      entry.data = toJsonValue(data);
    }
    this.steps.push(entry);
  }

  attach(name: string, content: string): void {
    this.attachments.push({ name: sanitizeFileName(name), content: content || "" });
  }

  async maybeWriteBundle(testInfo: TestInfo): Promise<void> {
    if (testInfo.status !== "failed" && testInfo.status !== "timedOut") {
      return;
    }
    await this.writeBundle(testInfo);
  }

  private async writeBundle(testInfo: TestInfo): Promise<void> {
    const endTime = new Date();
    const outputDir = process.env.BLACKBOX_OUTPUT_DIR || "blackbox-reports";
    const outputRoot = path.isAbsolute(outputDir)
      ? outputDir
      : path.resolve(process.cwd(), outputDir);
    const bundleName = `${this.testId}_${bundleTimestamp(endTime)}`;
    const bundleDir = path.join(outputRoot, bundleName);

    await fs.mkdir(bundleDir, { recursive: true });

    let attachmentsCreated = false;
    const attachmentsDir = path.join(bundleDir, "attachments");

    if (this.attachments.length > 0) {
      await fs.mkdir(attachmentsDir, { recursive: true });
      attachmentsCreated = true;
      const nameCounts = new Map<string, number>();
      for (const att of this.attachments) {
        const count = nameCounts.get(att.name) || 0;
        nameCounts.set(att.name, count + 1);
        let finalName = att.name;
        if (count > 0) {
          finalName = `${att.name}-${count}`;
        }
        await fs.writeFile(path.join(attachmentsDir, finalName), att.content, "utf-8");
      }
    }

    const durationMs = testInfo.duration ?? endTime.getTime() - this.startTime.getTime();
    const error = (testInfo.errors && testInfo.errors[0]) || (testInfo as any).error;
    const exceptionType = error && error.name ? error.name : "Error";
    const exceptionMessage = error && error.message ? error.message : "Test failed";
    const exceptionStack = error && error.stack ? error.stack : undefined;

    const manifest: any = {
      schemaVersion: 1,
      meta: {
        testId: this.testId,
        testName: this.testName,
        testClass: this.testClass,
        status: "FAILED",
        timestamp: endTime.toISOString(),
        durationMs: durationMs,
        runId: this.runId,
        framework: { name: "playwright-test", version: getPlaywrightVersion() },
        runtime: {
          language: "node",
          version: process.version.replace(/^v/, ""),
          os: `${os.platform()}`,
          arch: process.arch,
        },
      },
      context: this.context,
      steps: this.steps,
      exception: {
        type: exceptionType,
        message: exceptionMessage,
      },
      artifacts: {
        bundleDir: bundleName,
        logs: "context.log",
      },
    };

    if (exceptionStack) {
      manifest.exception.stackTrace = exceptionStack;
    }

    // Harden: check existence and type
    try {
      const stats = await fs.stat(attachmentsDir);
      if (stats.isDirectory()) {
        manifest.artifacts.attachmentsDir = "attachments/";
      }
    } catch {
      // ignore
    }

    const contextLog = this.buildContextLog(endTime, durationMs);
    await fs.writeFile(path.join(bundleDir, "context.log"), contextLog, "utf-8");
    await fs.writeFile(
      path.join(bundleDir, "manifest.json"),
      JSON.stringify(manifest, null, 2),
      "utf-8"
    );
  }

  private buildContextLog(endTime: Date, durationMs: number): string {
    const lines: string[] = [];
    lines.push("BlackBox context log");
    lines.push(`testClass=${this.testClass}`);
    lines.push(`testName=${this.testName}`);
    lines.push(`testId=${this.testId}`);
    lines.push(`runId=${this.runId}`);
    lines.push("status=FAILED");
    lines.push(`timestamp=${endTime.toISOString()}`);
    lines.push(`durationMs=${durationMs}`);
    lines.push("");
    lines.push("context:");
    if (Object.keys(this.context).length === 0) {
      lines.push("- (none)");
    } else {
      for (const [k, v] of Object.entries(this.context)) {
        lines.push(`- ${k}: ${JSON.stringify(v)}`);
      }
    }
    lines.push("");
    lines.push("steps:");
    if (this.steps.length === 0) {
      lines.push("- (none)");
    } else {
      for (const s of this.steps) {
        const extra = s.data !== undefined ? ` | data=${JSON.stringify(s.data)}` : "";
        lines.push(`- [${s.ts}] ${s.level} ${s.message}${extra}`);
      }
    }
    lines.push("");
    return lines.join("\n");
  }
}
