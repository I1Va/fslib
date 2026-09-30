"""
Grammar:
    union    := concat ('|' concat)*
    concat   := repeat*
    repeat   := atom ('*' | '+')*
    atom     := LITERAL | '.' | '(' union ')'
    LITERAL  := char
"""

from .ast import Concat, Epsilon, Literal, Plus, RegexNode, Star, Union, Wildcard
from .errors import RegexSyntaxError

_REPEAT_OPS = ("*", "+")


class RegexParser:
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self._eof:
            raise StopIteration
        return self._advance()

    @property
    def _eof(self) -> bool:
        return self.pos >= len(self.pattern)

    def _peek(self) -> str | None:
        return None if self._eof else self.pattern[self.pos]

    def _advance(self) -> str:
        char = self.pattern[self.pos]
        self.pos += 1
        return char

    def parse(self) -> RegexNode:
        node = self._parse_union()
        if not self._eof:
            char = self._peek()
            message = "unmatched ')'" if char == ")" else f"unexpected {char!r}"
            raise RegexSyntaxError(message, self.pattern, self.pos)
        return node

    def _parse_union(self) -> RegexNode:
        node = self._parse_concat()
        while self._peek() == "|":
            self._advance()
            node = Union(node, self._parse_concat())
        return node

    def _parse_concat(self) -> RegexNode:
        node: RegexNode | None = None
        while not self._eof and self._peek() not in ("|", ")"):
            term = self._parse_repeat()
            node = term if node is None else Concat(node, term)
        return node if node is not None else Epsilon()

    def _parse_repeat(self) -> RegexNode:
        node = self._parse_atom()
        while self._peek() in _REPEAT_OPS:
            op = self._advance()
            node = Star(node) if op == "*" else Plus(node)
        return node

    def _parse_atom(self) -> RegexNode:
        char = self._peek()
        if char in _REPEAT_OPS:
            raise RegexSyntaxError(f"nothing to repeat before {char!r}", self.pattern, self.pos)
        if char == "(":
            self._advance()
            node = self._parse_union()
            if self._peek() != ")":
                raise RegexSyntaxError("unbalanced '('", self.pattern, self.pos)
            self._advance()
            return node
        if char == ".":
            self._advance()
            return Wildcard()
        if char == "\\":
            self._advance()
            if self._eof:
                raise RegexSyntaxError("dangling escape '\\' at end of pattern", self.pattern, self.pos)
            return Literal(self._advance())
        self._advance()
        return Literal(char)


def parse(pattern: str) -> RegexNode:
    return RegexParser(pattern).parse()
