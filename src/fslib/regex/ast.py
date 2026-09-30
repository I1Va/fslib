from abc import ABC
from dataclasses import dataclass

# TODO: Убрать абстрактный класс. 
class RegexNode(ABC):
    """Base class for regex AST nodes"""


@dataclass(frozen=True)
class Epsilon(RegexNode):
    """Empty string class"""


@dataclass(frozen=True, slots=True) # TODO: почитать про slots
class Literal(RegexNode):
    char: str

    def __post_init__(self) -> None:
        if len(self.char) != 1:
            raise ValueError(f"Literal.char must be a single character, got {self.char!r}")


@dataclass(frozen=True)
class Wildcard(RegexNode):
    """'.' - any symbol from alphabet"""


@dataclass(frozen=True)
class Concat(RegexNode):
    left: RegexNode
    right: RegexNode


@dataclass(frozen=True)
class Union(RegexNode):
    left: RegexNode
    right: RegexNode


@dataclass(frozen=True)
class Star(RegexNode):
    child: RegexNode


@dataclass(frozen=True)
class Plus(RegexNode):
    child: RegexNode
