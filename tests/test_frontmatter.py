"""Mirrored tests for :code:`fedoup_frontmatter`.

Test names + inputs intentionally match the TypeScript sibling's
``frontmatter.test.ts`` so both sides catch the same regressions.
"""

from __future__ import annotations

from fedoup_frontmatter import parse, patch, serialize


# ---- parse --------------------------------------------------------------- #


def test_parse_returns_empty_frontmatter_for_plain_markdown() -> None:
    raw = "# Hello\n\nNo frontmatter here.\n"
    result = parse(raw)
    assert result.frontmatter == {}
    assert result.body == raw


def test_parse_basic_frontmatter_block() -> None:
    raw = """---
title: Hello
tags:
  - one
  - two
---

# Body
"""
    result = parse(raw)
    assert result.frontmatter == {"title": "Hello", "tags": ["one", "two"]}
    assert result.body == "# Body\n"


def test_parse_inline_list_and_typed_scalars() -> None:
    raw = """---
title: "Hello: world"
tags: [a, b, c]
count: 3
draft: true
---
body"""
    result = parse(raw)
    assert result.frontmatter == {
        "title": "Hello: world",
        "tags": ["a", "b", "c"],
        "count": 3,
        "draft": True,
    }
    assert result.body == "body"


def test_parse_doc_that_opens_with_dashes_but_never_closes() -> None:
    raw = "---\nkey: value\n# never closes\nbody"
    result = parse(raw)
    assert result.frontmatter == {}
    assert result.body == raw


def test_parse_ignores_dashes_that_arent_on_their_own_line() -> None:
    raw = "Some --- text\nwith dashes\n"
    result = parse(raw)
    assert result.frontmatter == {}
    assert result.body == raw


def test_parse_strips_a_single_leading_newline_from_body() -> None:
    raw = "---\nk: v\n---\n\n\nbody with two blanks above"
    result = parse(raw)
    assert result.body == "\nbody with two blanks above"


def test_parse_tolerates_utf8_bom() -> None:
    raw = "﻿---\ntitle: Hello\n---\n\nbody"
    result = parse(raw)
    assert result.frontmatter == {"title": "Hello"}
    assert result.body == "body"


def test_parse_handles_crlf_line_endings() -> None:
    raw = "---\r\ntitle: Hello\r\n---\r\n\r\nbody"
    result = parse(raw)
    assert result.frontmatter == {"title": "Hello"}
    assert result.body.endswith("body")


# ---- serialize ----------------------------------------------------------- #


def test_serialize_returns_body_verbatim_when_frontmatter_empty() -> None:
    out = serialize(frontmatter={}, body="# Hello\n")
    assert out == "# Hello\n"


def test_serialize_emits_fenced_yaml_block_followed_by_blank_line() -> None:
    out = serialize(frontmatter={"title": "Hello", "count": 3}, body="# Body\n")
    # PyYAML, like js-yaml, only quotes scalars when necessary; plain strings
    # stay unquoted. The TS sibling test mirrors this expectation.
    assert (
        out
        == """---
title: Hello
count: 3
---

# Body
"""
    )


def test_serialize_preserves_frontmatter_insertion_order() -> None:
    out = serialize(frontmatter={"z": 1, "a": 2, "m": 3}, body="")
    lines = out.split("\n")
    assert lines[1:4] == ["z: 1", "a: 2", "m: 3"]


# ---- patch --------------------------------------------------------------- #


def test_patch_updates_single_field_preserves_rest_and_body() -> None:
    raw = """---
title: Hello
status: draft
tags: [a, b]
---

# Body content
unchanged
"""
    out = patch(raw, {"status": "published"})
    reparsed = parse(out)
    assert reparsed.frontmatter["title"] == "Hello"
    assert reparsed.frontmatter["status"] == "published"
    assert reparsed.frontmatter["tags"] == ["a", "b"]
    assert reparsed.body == "# Body content\nunchanged\n"


def test_patch_adds_new_field_to_existing_frontmatter() -> None:
    raw = """---
title: Hello
---

body"""
    out = patch(raw, {"updated_at": "2026-05-28"})
    assert parse(out).frontmatter == {"title": "Hello", "updated_at": "2026-05-28"}


def test_patch_adds_frontmatter_to_doc_that_had_none() -> None:
    out = patch("plain body", {"title": "Added"})
    reparsed = parse(out)
    assert reparsed.frontmatter == {"title": "Added"}
    assert reparsed.body == "plain body"


# ---- round-trip ---------------------------------------------------------- #


def test_round_trip_byte_stable_for_canonical_input() -> None:
    raw = """---
title: Hello
count: 3
---

# Body
"""
    assert serialize(frontmatter=parse(raw).frontmatter, body=parse(raw).body) == raw


def test_round_trip_byte_stable_for_empty_frontmatter() -> None:
    raw = "# Just body\n\nsome more"
    result = parse(raw)
    assert serialize(frontmatter=result.frontmatter, body=result.body) == raw
