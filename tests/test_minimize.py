import itertools
import re

import pytest

from fslib.fsm import FSM
from fslib.passes.construct import thompson
from fslib.passes.determinize import determinize
from fslib.passes.minimize import minimize
from fslib.regex.parser import parse

_WORDS = ["".join(p) for n in range(4) for p in itertools.product("abc", repeat=n)]


def _redundant_dfa() -> FSM:
    return FSM(
        states={0, 1, 2},
        alphabet={"a", "b"},
        transitions={
            0: {"a": {1}, "b": {2}},
            1: {"a": {1}, "b": {1}},
            2: {"a": {2}, "b": {2}},
        },
        start=0,
        accepting={1, 2},
    )


def test_merges_equivalent_states():
    dfa = _redundant_dfa()
    minimized = minimize(dfa)
    assert len(minimized.states) == 2


def test_language_preserved_when_merging_equivalent_states():
    dfa = _redundant_dfa()
    minimized = minimize(dfa)
    for word in _WORDS:
        assert dfa.accepts(word) == minimized.accepts(word)


def test_output_is_deterministic_and_complete():
    minimized = minimize(_redundant_dfa())
    assert minimized.is_deterministic
    for state in minimized.states:
        for symbol in minimized.alphabet:
            assert len(minimized.transitions.get(state, {}).get(symbol, ())) == 1


def test_rejects_nondeterministic_input():
    nfa = thompson(parse("a|b"))
    with pytest.raises(ValueError, match="deterministic"):
        minimize(nfa)


def test_rejects_incomplete_input():
    incomplete = FSM(
        states={0, 1},
        alphabet={"a", "b"},
        transitions={0: {"a": {1}}},  # missing 'b' from 0, and everything from 1
        start=0,
        accepting={1},
    )
    with pytest.raises(ValueError, match="complete"):
        minimize(incomplete)


def test_drops_unreachable_states():
    dfa = FSM(
        states={0, 1, 2},
        alphabet={"a"},
        transitions={0: {"a": {0}}, 1: {"a": {1}}, 2: {"a": {2}}},  # 1, 2 unreachable from 0
        start=0,
        accepting=set(),
    )
    minimized = minimize(dfa)
    assert len(minimized.states) == 1


def test_third_from_last_symbol_pattern_needs_multiple_refinement_rounds():
    pattern = "(a|b)*a(a|b)(a|b)"
    dfa = determinize(thompson(parse(pattern)))
    minimized = minimize(dfa)
    assert len(minimized.states) < len(dfa.states)
    for word in ["".join(p) for n in range(6) for p in itertools.product("ab", repeat=n)]:
        assert minimized.accepts(word) == (re.fullmatch(pattern, word) is not None)


@pytest.mark.parametrize("pattern", ["a", "a|b", "a*", "a+", "(a|b)*abb", "a(b|c)*", "ab|c", "(ab)*"])
def test_full_pipeline_matches_python_re_oracle(pattern):
    minimized = minimize(determinize(thompson(parse(pattern))))
    for word in _WORDS:
        expected = re.fullmatch(pattern, word) is not None
        assert minimized.accepts(word) == expected, f"pattern={pattern!r} word={word!r}"


@pytest.mark.parametrize("pattern", ["a", "a|b", "a*", "a+", "(a|b)*abb", "a(b|c)*"])
def test_language_preserved_across_full_pipeline(pattern):
    nfa = thompson(parse(pattern))
    dfa = determinize(nfa)
    minimized = minimize(dfa)
    for word in _WORDS:
        assert nfa.accepts(word) == dfa.accepts(word) == minimized.accepts(word), f"pattern={pattern!r} word={word!r}"
