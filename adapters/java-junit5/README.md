# BlackBox JUnit 5 Adapter

## Install

Maven dependency (placeholder):

<dependency>
  <groupId>dev.blackbox</groupId>
  <artifactId>blackbox-junit5</artifactId>
  <version>0.1.0</version>
  <scope>test</scope>
</dependency>

## Usage

@ExtendWith(BlackBoxExtension.class)
class MyTest {
  @Test
  void fails() {
    BlackBox.log("user", "alice");
    BlackBox.step("start");
    BlackBox.attach("note.txt", "hello");
    Assertions.fail("boom");
  }
}

Note: the static API relies on the test thread (MVP constraint).

## TestId derivation

canonical = "{testClass}::{testName}"

- testClass: fully-qualified class name
- testName: method name if available, else display name
- testId: sha1(canonical).hexdigest().slice(0, 16)

## Output directory

Default: `blackbox-reports/`
Override: `-Dblackbox.outputDir=/path/to/output`
