# BlackBox JUnit 5 Adapter

## Prerequisites

- Java (JDK) 11+
- Maven 3.8+

## Install

This adapter is developed in-repo. It is not published as a Maven artifact yet.
Use it directly from this monorepo.

From the repo root:

```bash
cd adapters/java-junit5
mvn -v
```

## Usage

```java
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
```

Note: the static API relies on the current test thread (MVP constraint).

## Running tests

Run unit tests (must pass):

```bash
cd adapters/java-junit5
mvn test
```

Run the demo failing test (expected failure, emits bundle):

```bash
cd adapters/java-junit5
mvn -q -Dtest=SampleFailingTest test
```

## TestId derivation

`canonical = "{testClass}::{testName}"`

- `testClass`: fully-qualified class name
- `testName`: method name if available, else display name
- `testId`: `sha1(canonical).hexdigest().slice(0, 16)`

## Output directory

Default: `blackbox-reports/`

Override: `-Dblackbox.outputDir=/path/to/output`
