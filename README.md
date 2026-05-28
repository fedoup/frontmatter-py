# fedoup-frontmatter

Tiny YAML-frontmatter parser/serializer/patcher for markdown documents. Sibling of the TypeScript package [`@fedoup/frontmatter`](https://github.com/fedoup/frontmatter-ts) — same API shape, same byte-stable round trip on canonical input, so a vault of `.md` files written by one side round-trips through the other.

```sh
pip install fedoup-frontmatter
```

```python
from fedoup_frontmatter import parse, serialize, patch

raw = """---
title: Hello
status: draft
---

# Body content
"""

result = parse(raw)
result.frontmatter   # {'title': 'Hello', 'status': 'draft'}
result.body          # '# Body content\n'

# Round-trip is byte-stable for canonical input
serialize(frontmatter=result.frontmatter, body=result.body) == raw

# Patch a single field, leave the rest alone
patch(raw, {"status": "published"})
```

## API

```python
@dataclass
class ParseResult:
    frontmatter: dict[str, Any]
    body: str

def parse(raw: str) -> ParseResult: ...
def serialize(*, frontmatter: Mapping[str, Any], body: str) -> str: ...
def patch(raw: str, partial: Mapping[str, Any]) -> str: ...
```

- **`parse`** — returns `ParseResult(frontmatter={}, body=raw)` if the document doesn't open with a `---` line. A UTF-8 BOM is tolerated; CRLF endings are accepted but the body is not normalized.
- **`serialize`** — empty frontmatter returns the body verbatim (no `---\n---\n` no-op block). Key order is preserved from the input dict.
- **`patch`** — merges `partial` into the existing frontmatter. Body and unaffected fields are preserved. To delete a key, parse → mutate the dict → `serialize` directly.

## Power source

Uses [PyYAML](https://pyyaml.org/) under the hood — full YAML support (scalars, sequences, mappings, anchors). The minimal regex parsers you see in many vault tools have edge cases this avoids; the cost is the PyYAML dependency.

## Sibling: TypeScript

A matching JS/TS package at `@fedoup/frontmatter` exists. Same function names, same semantics. Test fixtures are mirrored between the two repos so behavior stays aligned.

## License

MIT
