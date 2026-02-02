package dev.blackbox;

import com.fasterxml.jackson.databind.JsonNode;

public final class BlackBox {
    private BlackBox() {
    }

    public static void log(String key, Object value) {
        BlackBoxExtension.State state = BlackBoxExtension.currentState();
        JsonNode node = ManifestWriter.toJsonNode(value);
        state.context.put(key, node);
    }

    public static void step(String message) {
        step(message, "INFO", null);
    }

    public static void step(String message, String level) {
        step(message, level, null);
    }

    public static void step(String message, String level, Object data) {
        BlackBoxExtension.State state = BlackBoxExtension.currentState();
        JsonNode node = data == null ? null : ManifestWriter.toJsonNode(data);
        state.steps.add(new BlackBoxExtension.StepRecord(level, message, node));
    }

    public static void attach(String name, String content) {
        BlackBoxExtension.State state = BlackBoxExtension.currentState();
        String safe = BundlePaths.sanitizeFileName(name);
        state.attachments.add(new BlackBoxExtension.Attachment(safe, content));
    }
}
