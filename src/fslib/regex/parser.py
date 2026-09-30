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


class _Cursor:
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.advance()

    @property
    def eof(self) -> bool:
        return self.pos >= len(self.pattern)

    def peek(self) -> str | None:
        return None if self.eof else self.pattern[self.pos]

    def advance(self) -> str:
        char = self.pattern[self.pos]
        self.pos += 1
        return char


def parse(pattern: str) -> RegexNode:
    cursor = _Cursor(pattern)
    node = _parse_union(cursor)
    if not cursor.eof:
        char = cursor.peek()
        message = "unmatched ')'" if char == ")" else f"unexpected {char!r}"
        raise RegexSyntaxError(message, pattern, cursor.pos)
    return node


def _parse_union(cursor: _Cursor) -> RegexNode:
    node = _parse_concat(cursor)
    while cursor.peek() == "|":
        cursor.advance()
        node = Union(node, _parse_concat(cursor))
    return node

# TODO: сделать класс с методами рекурсивного спуска вместо curesor. 
# Сделать init от строки , имеет метод parse

def _parse_concat(cursor: _Cursor) -> RegexNode:
    node: RegexNode | None = None
    while not cursor.eof and cursor.peek() not in ("|", ")"):
        term = _parse_repeat(cursor)
        node = term if node is None else Concat(node, term)
    return node if node is not None else Epsilon()


def _parse_repeat(cursor: _Cursor) -> RegexNode:
    node = _parse_atom(cursor)
    while cursor.peek() in _REPEAT_OPS:
        op = cursor.advance()
        node = Star(node) if op == "*" else Plus(node)
    return node


def _parse_atom(cursor: _Cursor) -> RegexNode:
    char = cursor.peek()
    if char in _REPEAT_OPS:
        raise RegexSyntaxError(f"nothing to repeat before {char!r}", cursor.pattern, cursor.pos)
    if char == "(":
        cursor.advance()
        node = _parse_union(cursor)
        if cursor.peek() != ")":
            raise RegexSyntaxError("unbalanced '('", cursor.pattern, cursor.pos)
        cursor.advance()
        return node
    if char == ".":
        cursor.advance()
        return Wildcard()
    if char == "\\":
        cursor.advance()
        if cursor.eof:
            raise RegexSyntaxError("dangling escape '\\' at end of pattern", cursor.pattern, cursor.pos)
        return Literal(cursor.advance())
    cursor.advance()
    return Literal(char)
