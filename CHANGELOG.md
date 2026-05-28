# Changelog

## [Unreleased]

### Added
- Initial release: `parse(raw)` → `ParseResult(frontmatter, body)`, `serialize(frontmatter=..., body=...)` → `str`, `patch(raw, partial)` → `str`.
- Powered by PyYAML under the hood. Full YAML scalar/sequence/mapping support.
- Mirrored fixture suite with the TypeScript sibling `@fedoup/frontmatter`.
