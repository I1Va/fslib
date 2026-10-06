from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

from fslib.fsm import EPSILON, State, Symbol

_META = set("|*+.()\\")


class Builder(Protocol):
    alphabet: frozenset[Symbol]

    def new_state(self) -> State: ...
    def add_edge(self, src: State, symbol: Symbol | None, dst: State) -> None: ...


class RegexNode(ABC):
    precedence = 3

    @abstractmethod
    def build(self, builder: Builder) -> tuple[State, State]: ...

    @abstractmethod
    def pattern(self) -> str: ...

    def literals(self) -> frozenset[str]:
        return frozenset()

    def _operand(self, child: "RegexNode", min_precedence: int) -> str:
        text = child.pattern()
        if not text or child.precedence < min_precedence:
            return f"({text})"
        return text


@dataclass(frozen=True)
class Epsilon(RegexNode):
    def build(self, builder: Builder) -> tuple[State, State]:
        start, accept = builder.new_state(), builder.new_state()
        builder.add_edge(start, EPSILON, accept)
        return start, accept

    def pattern(self) -> str:
        return ""


@dataclass(frozen=True, slots=True)
class Literal(RegexNode):
    char: str

    def __post_init__(self) -> None:
        if len(self.char) != 1:
            raise ValueError(f"Literal.char must be a single character, got {self.char!r}")

    def build(self, builder: Builder) -> tuple[State, State]:
        start, accept = builder.new_state(), builder.new_state()
        builder.add_edge(start, self.char, accept)
        return start, accept

    def pattern(self) -> str:
        if self.char in _META or self.char.isspace():
            return "\\" + self.char
        return self.char

    def literals(self) -> frozenset[str]:
        return frozenset({self.char})


@dataclass(frozen=True)
class Wildcard(RegexNode):
    def build(self, builder: Builder) -> tuple[State, State]:
        start, accept = builder.new_state(), builder.new_state()
        for symbol in builder.alphabet:
            builder.add_edge(start, symbol, accept)
        return start, accept

    def pattern(self) -> str:
        return "."


@dataclass(frozen=True)
class Concat(RegexNode):
    left: RegexNode
    right: RegexNode

    precedence = 1

    def build(self, builder: Builder) -> tuple[State, State]:
        start1, accept1 = self.left.build(builder)
        start2, accept2 = self.right.build(builder)
        builder.add_edge(accept1, EPSILON, start2)
        return start1, accept2

    def pattern(self) -> str:
        return self._operand(self.left, 1) + self._operand(self.right, 1)

    def literals(self) -> frozenset[str]:
        return self.left.literals() | self.right.literals()


@dataclass(frozen=True)
class Union(RegexNode):
    left: RegexNode
    right: RegexNode

    precedence = 0

    def build(self, builder: Builder) -> tuple[State, State]:
        start1, accept1 = self.left.build(builder)
        start2, accept2 = self.right.build(builder)
        start, accept = builder.new_state(), builder.new_state()
        builder.add_edge(start, EPSILON, start1)
        builder.add_edge(start, EPSILON, start2)
        builder.add_edge(accept1, EPSILON, accept)
        builder.add_edge(accept2, EPSILON, accept)
        return start, accept

    def pattern(self) -> str:
        return f"{self.left.pattern()}|{self.right.pattern()}"

    def literals(self) -> frozenset[str]:
        return self.left.literals() | self.right.literals()


@dataclass(frozen=True)
class Star(RegexNode):
    child: RegexNode

    precedence = 2

    def build(self, builder: Builder) -> tuple[State, State]:
        inner_start, inner_accept = self.child.build(builder)
        start, accept = builder.new_state(), builder.new_state()
        builder.add_edge(start, EPSILON, inner_start)
        builder.add_edge(start, EPSILON, accept)
        builder.add_edge(inner_accept, EPSILON, inner_start)
        builder.add_edge(inner_accept, EPSILON, accept)
        return start, accept

    def pattern(self) -> str:
        return self._operand(self.child, 3) + "*"

    def literals(self) -> frozenset[str]:
        return self.child.literals()


@dataclass(frozen=True)
class Plus(RegexNode):
    child: RegexNode

    precedence = 2

    def build(self, builder: Builder) -> tuple[State, State]:
        start, accept = self.child.build(builder)
        builder.add_edge(accept, EPSILON, start)
        return start, accept

    def pattern(self) -> str:
        return self._operand(self.child, 3) + "+"

    def literals(self) -> frozenset[str]:
        return self.child.literals()
