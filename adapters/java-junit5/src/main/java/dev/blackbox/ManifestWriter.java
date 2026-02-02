package dev.blackbox;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

final class ManifestWriter {
    static final ObjectMapper MAPPER = new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

    private static final String FRAMEWORK_NAME = "junit5";
    private static final String FRAMEWORK_VERSION = resolveJUnitVersion();

    static JsonNode toJsonNode(Object value) {
        return MAPPER.valueToTree(value);
    }

    static void writeFailureBundle(BlackBoxExtension.State state, Instant endTime, Throwable cause, String outputDir) {
        BundlePaths paths = BundlePaths.forFailure(outputDir, state.testId, endTime);
        try {
            Files.createDirectories(paths.bundleDir);
            writeContextLog(paths, state, endTime);
            writeAttachments(paths, state);
            writeManifest(paths, state, endTime, cause);
        } catch (IOException e) {
            throw new RuntimeException("Failed to write BlackBox bundle", e);
        }
    }

    private static void writeManifest(BundlePaths paths, BlackBoxExtension.State state, Instant endTime,
            Throwable cause) throws IOException {
        ObjectNode root = MAPPER.createObjectNode();
        root.put("schemaVersion", 1);

        ObjectNode meta = root.putObject("meta");
        meta.put("testId", state.testId);
        meta.put("testName", state.testName);
        meta.put("testClass", state.testClass);
        meta.put("status", "FAILED");
        meta.put("timestamp", endTime.toString());
        meta.put("durationMs", Duration.between(state.startTime, endTime).toMillis());
        meta.put("runId", state.runId);
        if (state.testMethod != null) {
            meta.put("testMethod", state.testMethod);
        }

        ObjectNode framework = meta.putObject("framework");
        framework.put("name", FRAMEWORK_NAME);
        framework.put("version", FRAMEWORK_VERSION);

        ObjectNode runtime = meta.putObject("runtime");
        runtime.put("language", "java");
        runtime.put("version", System.getProperty("java.version"));
        runtime.put("os", System.getProperty("os.name"));
        runtime.put("arch", System.getProperty("os.arch"));

        ObjectNode context = root.putObject("context");
        for (Map.Entry<String, JsonNode> entry : state.context.entrySet()) {
            context.set(entry.getKey(), entry.getValue());
        }

        ArrayNode steps = root.putArray("steps");
        for (BlackBoxExtension.StepRecord step : state.steps) {
            ObjectNode s = steps.addObject();
            s.put("ts", step.ts.toString());
            s.put("level", step.level);
            s.put("message", step.message);
            if (step.data != null) {
                s.set("data", step.data);
            }
        }

        ObjectNode exception = root.putObject("exception");
        String type = cause != null ? cause.getClass().getName() : "java.lang.AssertionError";
        String message = cause != null && cause.getMessage() != null ? cause.getMessage() : "";
        exception.put("type", type);
        exception.put("message", message);
        if (cause != null) {
            exception.put("stackTrace", stackTrace(cause));
        }

        ObjectNode artifacts = root.putObject("artifacts");
        artifacts.put("bundleDir", paths.bundleDirName);
        artifacts.put("logs", "context.log");
        if (Files.isDirectory(paths.attachmentsDir)) {
            artifacts.put("attachmentsDir", "attachments/");
        }

        String json = MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(root);
        Files.writeString(paths.manifestPath, json, StandardCharsets.UTF_8);
    }

    private static void writeContextLog(BundlePaths paths, BlackBoxExtension.State state, Instant endTime)
            throws IOException {
        StringBuilder sb = new StringBuilder();
        sb.append("BlackBox context log\n");
        sb.append("testClass=").append(state.testClass).append("\n");
        sb.append("testName=").append(state.testName).append("\n");
        sb.append("testId=").append(state.testId).append("\n");
        sb.append("runId=").append(state.runId).append("\n");
        sb.append("status=FAILED\n");
        sb.append("timestamp=").append(endTime).append("\n");
        sb.append("durationMs=").append(Duration.between(state.startTime, endTime).toMillis()).append("\n\n");

        sb.append("context:\n");
        if (state.context.isEmpty()) {
            sb.append("- (none)\n");
        } else {
            for (Map.Entry<String, JsonNode> entry : state.context.entrySet()) {
                sb.append("- ").append(entry.getKey()).append(": ");
                sb.append(MAPPER.writeValueAsString(entry.getValue())).append("\n");
            }
        }

        sb.append("\nsteps:\n");
        if (state.steps.isEmpty()) {
            sb.append("- (none)\n");
        } else {
            for (BlackBoxExtension.StepRecord step : state.steps) {
                sb.append("- [").append(step.ts).append("] ");
                sb.append(step.level).append(" ").append(step.message);
                if (step.data != null) {
                    sb.append(" | data=").append(MAPPER.writeValueAsString(step.data));
                }
                sb.append("\n");
            }
        }

        Files.writeString(paths.contextLogPath, sb.toString(), StandardCharsets.UTF_8);
    }

    private static void writeAttachments(BundlePaths paths, BlackBoxExtension.State state) throws IOException {
        if (state.attachments.isEmpty()) {
            return;
        }
        Files.createDirectories(paths.attachmentsDir);
        Map<String, Integer> nameCounts = new LinkedHashMap<>();
        for (BlackBoxExtension.Attachment att : state.attachments) {
            String safe = BundlePaths.sanitizeFileName(att.name);
            Integer count = nameCounts.get(safe);
            nameCounts.put(safe, count == null ? 1 : count + 1);
            String finalName = safe;
            if (count != null) {
                finalName = safe + "-" + count;
            }
            Files.writeString(paths.attachmentsDir.resolve(finalName), att.content, StandardCharsets.UTF_8);
        }
    }

    private static String stackTrace(Throwable t) {
        StringWriter sw = new StringWriter();
        t.printStackTrace(new PrintWriter(sw));
        return sw.toString();
    }

    private static String resolveJUnitVersion() {
        Package pkg = org.junit.jupiter.api.Test.class.getPackage();
        String v = pkg.getImplementationVersion();
        return v != null ? v : "unknown";
    }
}
