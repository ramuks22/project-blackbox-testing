package dev.blackbox;

import org.junit.jupiter.api.Test;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;

import static org.junit.jupiter.api.Assertions.*;

class BundlePathsTest {

    // -----------------------------------------------------------------------
    // sanitizeFileName
    // -----------------------------------------------------------------------
    @Test
    void sanitizeFileName_normalName() {
        assertEquals("note.txt", BundlePaths.sanitizeFileName("note.txt"));
    }

    @Test
    void sanitizeFileName_preservesSafeChars() {
        assertEquals("file-name_v2.txt", BundlePaths.sanitizeFileName("file-name_v2.txt"));
    }

    @Test
    void sanitizeFileName_specialCharsReplaced() {
        String result = BundlePaths.sanitizeFileName("../../etc/passwd");
        assertFalse(result.contains("/"));
    }

    @Test
    void sanitizeFileName_emptyReturnsAttachment() {
        assertEquals("attachment", BundlePaths.sanitizeFileName(""));
    }

    @Test
    void sanitizeFileName_nullReturnsAttachment() {
        assertEquals("attachment", BundlePaths.sanitizeFileName(null));
    }

    @Test
    void sanitizeFileName_spacesReplaced() {
        String result = BundlePaths.sanitizeFileName("my file.txt");
        assertFalse(result.contains(" "));
    }

    // -----------------------------------------------------------------------
    // forFailure — bundle directory naming
    // -----------------------------------------------------------------------
    @Test
    void forFailure_correctBundleDirName() {
        Instant ts = Instant.parse("2026-02-02T14:30:00Z");
        BundlePaths paths = BundlePaths.forFailure("blackbox-reports", "abcdef0123456789", ts);
        assertEquals("abcdef0123456789_20260202T143000Z", paths.bundleDirName);
    }

    @Test
    void forFailure_manifestAndContextPaths() {
        Instant ts = Instant.parse("2026-01-01T00:00:00Z");
        BundlePaths paths = BundlePaths.forFailure("blackbox-reports", "aaaa0000bbbb1111", ts);
        assertTrue(paths.manifestPath.toString().endsWith("manifest.json"));
        assertTrue(paths.contextLogPath.toString().endsWith("context.log"));
        assertTrue(paths.attachmentsDir.toString().endsWith("attachments"));
    }

    @Test
    void forFailure_midnightTimestamp() {
        Instant ts = Instant.parse("2026-01-01T00:00:00Z");
        BundlePaths paths = BundlePaths.forFailure("output", "aabbccdd11223344", ts);
        assertEquals("aabbccdd11223344_20260101T000000Z", paths.bundleDirName);
    }

    @Test
    void forFailure_endOfDayTimestamp() {
        Instant ts = Instant.parse("2026-12-31T23:59:59Z");
        BundlePaths paths = BundlePaths.forFailure("output", "aabbccdd11223344", ts);
        assertEquals("aabbccdd11223344_20261231T235959Z", paths.bundleDirName);
    }

    // -----------------------------------------------------------------------
    // resolveOutputRoot
    // -----------------------------------------------------------------------
    @Test
    void resolveOutputRoot_absolutePathPassedThrough() {
        Path result = BundlePaths.resolveOutputRoot("/tmp/output");
        assertTrue(result.isAbsolute());
        assertEquals(Paths.get("/tmp/output"), result);
    }

    @Test
    void resolveOutputRoot_relativePathResolved() {
        Path result = BundlePaths.resolveOutputRoot("blackbox-reports");
        assertTrue(result.isAbsolute());
        assertTrue(result.toString().endsWith("blackbox-reports"));
    }
}
