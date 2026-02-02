package dev.blackbox;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;

final class BundlePaths {
    static final String DEFAULT_OUTPUT_DIR = "blackbox-reports";

    private static final DateTimeFormatter BUNDLE_TS =
            DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss'Z'").withZone(ZoneOffset.UTC);

    final Path outputRoot;
    final Path bundleDir;
    final Path manifestPath;
    final Path contextLogPath;
    final Path attachmentsDir;
    final String bundleDirName;

    private BundlePaths(Path outputRoot, Path bundleDir, String bundleDirName) {
        this.outputRoot = outputRoot;
        this.bundleDir = bundleDir;
        this.manifestPath = bundleDir.resolve("manifest.json");
        this.contextLogPath = bundleDir.resolve("context.log");
        this.attachmentsDir = bundleDir.resolve("attachments");
        this.bundleDirName = bundleDirName;
    }

    static BundlePaths forFailure(String outputDir, String testId, Instant timestamp) {
        String bundleDirName = testId + "_" + BUNDLE_TS.format(timestamp);
        Path outputRoot = resolveOutputRoot(outputDir);
        Path bundleDir = outputRoot.resolve(bundleDirName);
        return new BundlePaths(outputRoot, bundleDir, bundleDirName);
    }

    static Path resolveOutputRoot(String outputDir) {
        Path root = Paths.get(outputDir);
        if (!root.isAbsolute()) {
            root = Paths.get(System.getProperty("user.dir")).resolve(root).normalize();
        }
        return root;
    }

    static String sanitizeFileName(String name) {
        if (name == null || name.isEmpty()) {
            return "attachment";
        }
        String safe = name.replaceAll("[^A-Za-z0-9._-]", "_");
        if (safe.isEmpty()) {
            return "attachment";
        }
        return safe;
    }
}
