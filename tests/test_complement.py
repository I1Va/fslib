import itertools

import pytest

from fslib.fsm import FSM
from fslib.passes.complement import complement
from fslib.passes.construct import thompson
from fslib.passes.determinize import determinize
from fslib.passes.minimize import minimize
from fslib.regex.parser import parse

def _words_over(alphabet: frozenset[str]) -> list[str]:
    symbols = sorted(alphabet) or ["a"]
    return ["".join(p) for n in range(5) for p in itertools.product(symbols, repeat=n)]


@pytest.mark.parametrize("pattern", ["a", "a|b", "a*", "a+", "(a|b)*abb", "a(b|c)*", "ab|c", "(ab)*"])
def test_complement_flips_every_word(pattern):
    dfa = minimize(determinize(thompson(parse(pattern))))
    co = complement(dfa)
    for word in _words_over(dfa.alphabet):
        assert co.accepts(word) == (not dfa.accepts(word))


def test_double_complement_restores_language():
    dfa = minimize(determinize(thompson(parse("(a|b)*abb"))))
    twice = complement(complement(dfa))
    for word in _words_over(dfa.alphabet):
        assert twice.accepts(word) == dfa.accepts(word)


def test_complement_over_explicit_alphabet():
    dfa = minimize(determinize(thompson(parse("a*"), frozenset("ab"))))
    co = complement(dfa)
    assert co.accepts("b")
    assert co.accepts("ab")
    assert not co.accepts("")
    assert not co.accepts("aaa")


def test_accepts_nondeterministic_input():
    nfa = thompson(parse("aa|ab"))
    co = complement(nfa)
    for word in _words_over(nfa.alphabet):
        assert co.accepts(word) == (not nfa.accepts(word))


def test_accepts_incomplete_input():
    incomplete = FSM(
        states={0, 1},
        alphabet={"a", "b"},
        transitions={0: {"a": {1}}},
        start=0,
        accepting={1},
    )
    co = complement(incomplete)
    assert co.accepts("")
    assert co.accepts("b")
    assert co.accepts("aa")
    assert not co.accepts("a")
