import itertools
import re

import pytest

from fslib.passes.construct import thompson
from fslib.passes.determinize import determinize
from fslib.regex.ast import Literal, Union
from fslib.regex.parser import parse

_WORDS = ["".join(p) for n in range(4) for p in itertools.product("abc", repeat=n)]


def test_output_is_deterministic_and_epsilon_free():
    nfa = thompson(parse("a(b|c)*"))
    dfa = determinize(nfa)
    assert dfa.is_deterministic
    assert dfa.is_epsilon_free


def test_output_is_complete():
    nfa = thompson(parse("a(b|c)*"))
    dfa = determinize(nfa)
    for state in dfa.states:
        for symbol in dfa.alphabet:
            assert len(dfa.transitions.get(state, {}).get(symbol, ())) == 1


def test_dead_state_is_reached_and_self_loops():
    dfa = determinize(thompson(Literal("a")))
    assert dfa.accepts("a")
    assert not dfa.accepts("aa")
    assert not dfa.accepts("aaaa")


@pytest.mark.parametrize("pattern", ["a", "a|b", "a*", "a+", "(a|b)*abb", "a(b|c)*", "ab|c"])
def test_language_preserved_across_determinize(pattern):
    nfa = thompson(parse(pattern))
    dfa = determinize(nfa)
    for word in _WORDS:
        assert nfa.accepts(word) == dfa.accepts(word), f"pattern={pattern!r} word={word!r}"


@pytest.mark.parametrize("pattern", ["a", "a|b", "a*", "a+", "(a|b)*abb", "a(b|c)*", "ab|c"])
def test_matches_python_re_oracle(pattern):
    dfa = determinize(thompson(parse(pattern)))
    for word in _WORDS:
        expected = re.fullmatch(pattern, word) is not None
        assert dfa.accepts(word) == expected, f"pattern={pattern!r} word={word!r}"


def test_union_of_two_letters_accepts_exactly_those():
    dfa = determinize(thompson(Union(Literal("a"), Literal("b"))))
    assert dfa.accepts("a")
    assert dfa.accepts("b")
    assert not dfa.accepts("")
    assert not dfa.accepts("ab")
    assert not dfa.accepts("c")


def test_empty_alphabet_nfa_determinizes_to_single_state():
    from fslib.regex.ast import Epsilon

    dfa = determinize(thompson(Epsilon()))
    assert dfa.alphabet == frozenset()
    assert dfa.accepts("")
    assert dfa.states == frozenset({0})
