# Versioning

- The spec is authoritative. `spec/manifest.schema.json` and `spec/bundle-layout.md` define the contract.
- Breaking changes require bumping `schemaVersion` in the manifest schema.
- Non-breaking changes can be released as adapter minor/patch versions without changing `schemaVersion`.
- Adapters must remain compliant with the current `schemaVersion`.
