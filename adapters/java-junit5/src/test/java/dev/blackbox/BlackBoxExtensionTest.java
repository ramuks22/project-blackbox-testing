package dev.blackbox;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class BlackBoxExtensionTest {

    // -----------------------------------------------------------------------
    // StepRecord level normalization
    // -----------------------------------------------------------------------
    @Test
    void stepRecord_infoLevel() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord("INFO", "msg", null);
        assertEquals("INFO", rec.level);
    }

    @Test
    void stepRecord_debugLevel() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord("DEBUG", "msg", null);
        assertEquals("DEBUG", rec.level);
    }

    @Test
    void stepRecord_warnLevel() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord("WARN", "msg", null);
        assertEquals("WARN", rec.level);
    }

    @Test
    void stepRecord_errorLevel() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord("ERROR", "msg", null);
        assertEquals("ERROR", rec.level);
    }

    @Test
    void stepRecord_nullDefaultsToInfo() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord(null, "msg", null);
        assertEquals("INFO", rec.level);
    }

    @Test
    void stepRecord_unknownLevelDefaultsToInfo() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord("TRACE", "msg", null);
        assertEquals("INFO", rec.level);
    }

    @Test
    void stepRecord_lowercaseNormalized() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord("warn", "msg", null);
        assertEquals("WARN", rec.level);
    }

    @Test
    void stepRecord_timestampIsSet() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord("INFO", "msg", null);
        assertNotNull(rec.ts);
    }

    @Test
    void stepRecord_messagePreserved() {
        BlackBoxExtension.StepRecord rec = new BlackBoxExtension.StepRecord("INFO", "hello world", null);
        assertEquals("hello world", rec.message);
    }
}
