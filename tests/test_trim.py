import itertools
import re

import pytest

from fslib.fsm import FSM
from fslib.passes.construct import _Builder, thompson
from fslib.passes.trim import trim
from fslib.regex.parser import parse

_WORDS = ["".join(p) for n in range(5) for p in itertools.product("abc", repeat=n)]


def _edge_count(fsm: FSM) -> int:
    return sum(len(targets) for edges in fsm.transitions.values() for targets in edges.values())


def _raw_thompson(pattern: str) -> FSM:
    """Build the untrimmed Thompson NFA, bypassing thompson()'s default trim() call."""
    ast = parse(pattern)
    alphabet = ast.literals()
    builder = _Builder(alphabet)
    start, accept = ast.build(builder)
    return FSM(
        states=frozenset(builder.states),
        alphabet=alphabet,
        transitions=builder.transitions,
        start=start,
        accepting=frozenset({accept}),
    )


def test_thompson_applies_trim_by_default():
    raw = _raw_thompson("a(a(ab)*a(ab)*|b)*")
    assert thompson(parse("a(a(ab)*a(ab)*|b)*")).states == trim(raw).states


def test_collapses_pass_through_states():
    nfa = _raw_thompson("a(a(ab)*a(ab)*|b)*")
    reduced = trim(nfa)
    assert len(reduced.states) < len(nfa.states)
    assert _edge_count(reduced) < _edge_count(nfa)


def test_does_not_accept_empty_string_for_plus():
    nfa = _raw_thompson("a+")
    reduced = trim(nfa)
    assert not reduced.accepts("")
    assert reduced.accepts("a")
    assert reduced.accepts("aaa")


def test_never_grows_states_or_edges():
    for pattern in ["a", "a|b", "a*", "a+", "(a|b)*abb", "a(b|c)*", "ab|c", "(ab)*", "(a|b)+"]:
        nfa = _raw_thompson(pattern)
        reduced = trim(nfa)
        assert len(reduced.states) <= len(nfa.states)
        assert _edge_count(reduced) <= _edge_count(nfa)


@pytest.mark.parametrize(
    "pattern",
    ["a", "a|b", "a*", "a+", "(a|b)*abb", "a(b|c)*", "ab|c", "(ab)*", "a*b*c*", "(a|b|c)*abc", "a(a(ab)*a(ab)*|b)*"],
)
def test_language_preserved(pattern):
    nfa = _raw_thompson(pattern)
    reduced = trim(nfa)
    for word in _WORDS:
        assert nfa.accepts(word) == reduced.accepts(word) == (re.fullmatch(pattern, word) is not None), (
            pattern,
            word,
        )
