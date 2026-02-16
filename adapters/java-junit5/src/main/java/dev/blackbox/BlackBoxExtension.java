package dev.blackbox;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.extension.AfterEachCallback;
import org.junit.jupiter.api.extension.BeforeEachCallback;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.extension.TestWatcher;

import java.lang.reflect.Method;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

public class BlackBoxExtension implements BeforeEachCallback, AfterEachCallback, TestWatcher {
    private static final ExtensionContext.Namespace NAMESPACE = ExtensionContext.Namespace
            .create(BlackBoxExtension.class);
    private static final String STATE_KEY = "blackbox.state";
    private static final String RUN_ID = UUID.randomUUID().toString();
    private static final ThreadLocal<ExtensionContext> CURRENT = new ThreadLocal<>();

    @Override
    public void beforeEach(ExtensionContext context) {
        State state = getOrCreateState(context);
        state.startTime = Instant.now();
        CURRENT.set(context);
    }

    @Override
    public void afterEach(ExtensionContext context) {
        CURRENT.remove();
    }

    @Override
    public void testFailed(ExtensionContext context, Throwable cause) {
        State state = getOrCreateState(context);
        Instant endTime = Instant.now();
        ManifestWriter.writeFailureBundle(state, endTime, cause, outputDir());
    }

    static State currentState() {
        ExtensionContext context = CURRENT.get();
        if (context == null) {
            throw new IllegalStateException("BlackBoxExtension is not active on the current thread");
        }
        return getOrCreateState(context);
    }

    private static State getOrCreateState(ExtensionContext context) {
        return context.getStore(NAMESPACE).getOrComputeIfAbsent(STATE_KEY, k -> new State(context), State.class);
    }

    private static String outputDir() {
        return System.getProperty("blackbox.outputDir", BundlePaths.DEFAULT_OUTPUT_DIR);
    }

    static final class State {
        final Map<String, JsonNode> context = new LinkedHashMap<>();
        final List<StepRecord> steps = new ArrayList<>();
        final List<Attachment> attachments = new ArrayList<>();
        final String runId;
        final String testClass;
        final String testName;
        final String testMethod;
        final String testId;
        Instant startTime;

        State(ExtensionContext context) {
            this.runId = RUN_ID;
            this.testClass = context.getRequiredTestClass().getName();
            Optional<Method> method = context.getTestMethod();
            this.testMethod = method.map(Method::getName).orElse(null);
            this.testName = method.map(Method::getName).orElse(context.getDisplayName());
            this.testId = sha1Hex16(testClass + "::" + testName);
        }
    }

    static final class StepRecord {
        final Instant ts;
        final String level;
        final String message;
        final JsonNode data;

        StepRecord(String level, String message, JsonNode data) {
            this.ts = Instant.now();
            this.level = normalizeLevel(level);
            this.message = message;
            this.data = data;
        }

        private static String normalizeLevel(String level) {
            if (level == null) {
                return "INFO";
            }
            String upper = level.toUpperCase();
            switch (upper) {
                case "DEBUG":
                case "INFO":
                case "WARN":
                case "ERROR":
                    return upper;
                default:
                    return "INFO";
            }
        }
    }

    static final class Attachment {
        final String name;
        final String content;

        Attachment(String name, String content) {
            this.name = name;
            this.content = content == null ? "" : content;
        }
    }

    private static String sha1Hex16(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            byte[] digest = md.digest(input.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString().substring(0, 16);
        } catch (Exception e) {
            throw new RuntimeException("Failed to compute sha1", e);
        }
    }
}
