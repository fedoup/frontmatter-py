"""Frontmatter parse / serialize / patch.

Sibling of the TypeScript ``@fedoup/frontmatter`` package — same opening
``---`` line convention, same body-after-newline rule, same patch semantics.
A vault of ``.md`` files written by one side round-trips byte-for-byte through
the other for the canonical case.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import yaml

_OPEN = "---"
# Closing fence: a `---` on its own line, with optional trailing whitespace,
# terminated by either a newline or EOF. Matches the multi-line scan that the
# TS sibling does with `^---[ \t]*$` (m flag).
_CLOSE_RE = re.compile(r"\r?\n---[ \t]*(?:\r?\n|$)")


@dataclass
class ParseResult:
    """A parsed markdown document split into frontmatter + body.

    Returned by :func:`parse`. ``frontmatter`` is always a ``dict`` (empty if
    the document doesn't open with ``---``). ``body`` is the content after
    the closing ``---`` line, with at most one leading newline consumed so
    a round trip through :func:`serialize` doesn't grow newlines.
    """

    frontmatter: dict[str, Any]
    body: str


def parse(raw: str) -> ParseResult:
    """Parse a markdown document with optional YAML frontmatter.

    >>> parse("---\\ntitle: Hello\\n---\\n\\nbody").frontmatter
    {'title': 'Hello'}
    >>> parse("plain body").frontmatter
    {}

    The leading line must be exactly ``---`` (no leading whitespace) for the
    frontmatter mode to engage. A UTF-8 BOM is tolerated.
    """
    s = raw
    if s.startswith("﻿"):
        s = s[1:]

    if not (s.startswith(f"{_OPEN}\n") or s.startswith(f"{_OPEN}\r\n")):
        return ParseResult(frontmatter={}, body=raw)

    after_open_nl = s.index("\n") + 1
    close_match = _CLOSE_RE.search(s, after_open_nl)
    if close_match is None:
        return ParseResult(frontmatter={}, body=raw)

    yaml_source = s[after_open_nl : close_match.start()]
    body_start = close_match.end()
    body = s[body_start:]
    if body.startswith("\n"):
        body = body[1:]

    loaded = yaml.safe_load(yaml_source) if yaml_source.strip() else {}
    if not isinstance(loaded, dict):
        # Malformed frontmatter (e.g. a list at top level) — treat as no
        # frontmatter, return the raw document. Avoids surprising the caller
        # with a partial parse.
        return ParseResult(frontmatter={}, body=raw)

    return ParseResult(frontmatter=loaded, body=body)


def serialize(*, frontmatter: Mapping[str, Any], body: str) -> str:
    """Build a markdown document from ``frontmatter`` + ``body``.

    If ``frontmatter`` has no keys, returns ``body`` unchanged — round-tripping
    a plain-body document gives back the plain body, not a ``---\\n---\\n``
    no-op block.
    """
    if not frontmatter:
        return body
    yaml_block = yaml.safe_dump(
        dict(frontmatter),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=10_000,
    ).rstrip("\n")
    return f"{_OPEN}\n{yaml_block}\n{_OPEN}\n\n{body}"


def patch(raw: str, partial: Mapping[str, Any]) -> str:
    """Merge ``partial`` into the existing frontmatter and re-serialize.

    Body and unaffected fields are preserved. Setting a key to ``None`` keeps
    the key as null in the output — to delete a key, parse, mutate the dict,
    and call :func:`serialize` directly.
    """
    parsed = parse(raw)
    next_fm = dict(parsed.frontmatter)
    next_fm.update(dict(partial))
    return serialize(frontmatter=next_fm, body=parsed.body)
