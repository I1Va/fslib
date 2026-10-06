import itertools

import pytest

from fslib.fsm import FSM
from fslib.passes.complement import complement
from fslib.passes.construct import thompson
from fslib.passes.determinize import determinize
from fslib.passes.minimize import minimize
from fslib.passes.to_regex import fsm_to_regex
from fslib.regex.parser import parse

_PATTERNS = ["a", "ab", "a|b", "a*", "a+", "(a|b)*abb", "a(b|c)*", "ab|c", "(ab)*", "a*b*", "", "(b(a|b)a*)+(ba)*ba+"]


def _words(alphabet):
    symbols = sorted(alphabet) or ["a"]
    return ["".join(p) for n in range(8) for p in itertools.product(symbols, repeat=n)]


def _minimal(pattern, alphabet=None):
    return minimize(determinize(thompson(parse(pattern), alphabet)))


@pytest.mark.parametrize("pattern", _PATTERNS)
def test_round_trip_preserves_language(pattern):
    original = _minimal(pattern)
    recovered = _minimal(fsm_to_regex(original).pattern(), original.alphabet)
    for word in _words(original.alphabet):
        assert recovered.accepts(word) == original.accepts(word)


@pytest.mark.parametrize("pattern", _PATTERNS)
def test_round_trip_preserves_minimal_size(pattern):
    original = _minimal(pattern)
    recovered = _minimal(fsm_to_regex(original).pattern(), original.alphabet)
    assert len(recovered.states) == len(original.states)


def test_works_on_a_raw_nfa_with_epsilon_edges():
    nfa = thompson(parse("(a|b)*ab"))
    recovered = _minimal(fsm_to_regex(nfa).pattern(), nfa.alphabet)
    for word in _words(nfa.alphabet):
        assert recovered.accepts(word) == nfa.accepts(word)


def test_complement_as_a_regex():
    original = _minimal("a*", frozenset("ab"))
    co_pattern = fsm_to_regex(complement(original)).pattern()
    recovered = _minimal(co_pattern, frozenset("ab"))
    for word in _words("ab"):
        assert recovered.accepts(word) == (not original.accepts(word))


def test_empty_language_has_no_pattern():
    universal = _minimal("(a|b)*", frozenset("ab"))
    with pytest.raises(ValueError, match="empty"):
        fsm_to_regex(complement(universal))


def test_unreachable_and_dead_states_are_ignored():
    fsm = FSM(
        states={0, 1, 2, 3},
        alphabet={"a"},
        transitions={0: {"a": {1}}, 2: {"a": {2}}, 1: {"a": {3}}, 3: {"a": {3}}},
        start=0,
        accepting={1},
    )
    assert fsm_to_regex(fsm).pattern() == "a"
