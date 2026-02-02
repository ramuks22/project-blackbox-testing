package dev.blackbox;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(BlackBoxExtension.class)
class SampleFailingTest {
    @Test
    void sampleFailure() {
        BlackBox.log("user", "alice");
        BlackBox.step("start");
        BlackBox.attach("note.txt", "hello");
        Assertions.assertEquals(1, 2, "boom");
    }
}
