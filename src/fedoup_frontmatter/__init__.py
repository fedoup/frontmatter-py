"""Tiny YAML-frontmatter parser/serializer/patcher for markdown documents.

Mirrors the API of the TypeScript sibling :code:`@fedoup/frontmatter` — same
function names, same behavior, same byte-stable round trip on canonical input.
"""

from __future__ import annotations

from .frontmatter import ParseResult, parse, patch, serialize

__all__ = ["ParseResult", "parse", "patch", "serialize"]
__version__ = "0.1.0"
