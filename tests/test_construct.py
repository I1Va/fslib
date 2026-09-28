import itertools
import re

import pytest

from fslib.passes.construct import _Builder, thompson
from fslib.regex.ast import Concat, Epsilon, Literal, Plus, Star, Union, Wildcard
from fslib.regex.parser import parse


def test_epsilon_accepts_only_empty_string():
    fsm = thompson(Epsilon())
    assert fsm.accepts("")
    assert not fsm.accepts("a")


def test_single_literal():
    fsm = thompson(Literal("a"))
    assert fsm.accepts("a")
    assert not fsm.accepts("")
    assert not fsm.accepts("b")
    assert not fsm.accepts("aa")


def test_concat():
    fsm = thompson(Concat(Literal("a"), Literal("b")))
    assert fsm.accepts("ab")
    assert not fsm.accepts("a")
    assert not fsm.accepts("ba")
    assert not fsm.accepts("")


def test_union():
    fsm = thompson(Union(Literal("a"), Literal("b")))
    assert fsm.accepts("a")
    assert fsm.accepts("b")
    assert not fsm.accepts("ab")
    assert not fsm.accepts("")


def test_star():
    fsm = thompson(Star(Literal("a")))
    assert fsm.accepts("")
    assert fsm.accepts("a")
    assert fsm.accepts("aaaa")
    assert not fsm.accepts("b")
    assert not fsm.accepts("aab")


def test_plus_requires_at_least_one():
    fsm = thompson(Plus(Literal("a")))
    assert not fsm.accepts("")
    assert fsm.accepts("a")
    assert fsm.accepts("aaa")
    assert not fsm.accepts("aab")


def test_wildcard_alone_has_empty_alphabet_and_accepts_nothing():
    fsm = thompson(Wildcard())
    assert fsm.alphabet == frozenset()
    assert not fsm.accepts("a")
    assert not fsm.accepts("")


def test_wildcard_matches_any_inferred_alphabet_symbol():
    # alphabet is inferred from the whole AST, so '.' here ranges over {a, b}
    fsm = thompson(parse("a.b"))
    assert fsm.alphabet == frozenset({"a", "b"})
    assert fsm.accepts("aab")
    assert fsm.accepts("abb")
    assert not fsm.accepts("acb")
    assert not fsm.accepts("ab")


def test_result_is_nfa_shaped():
    fsm = thompson(parse("a|b"))
    assert not fsm.is_epsilon_free
    assert not fsm.is_deterministic


def test_unknown_node_type_raises():
    class NotARealNode:
        pass

    with pytest.raises(TypeError):
        _Builder(frozenset()).build(NotARealNode())  # type: ignore[arg-type]


_ORACLE_PATTERNS = [
    "a",
    "ab",
    "a|b",
    "a*",
    "a+",
    "(a|b)c",
    "ab|c",
    "(ab)*",
    "a(b|c)*",
    "(a|b)*abb",
    "a*b*",
    "",
]
_ORACLE_WORDS = ["".join(p) for n in range(4) for p in itertools.product("abc", repeat=n)]


@pytest.mark.parametrize("pattern", _ORACLE_PATTERNS)
def test_matches_python_re_oracle(pattern):
    fsm = thompson(parse(pattern))
    for word in _ORACLE_WORDS:
        expected = re.fullmatch(pattern, word) is not None
        assert fsm.accepts(word) == expected, f"pattern={pattern!r} word={word!r}"
