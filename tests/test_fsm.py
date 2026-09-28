import pytest

from fslib.fsm import EPSILON, FSM


def _ends_in_a() -> FSM:
    return FSM(
        states={0, 1},
        alphabet={"a", "b"},
        transitions={
            0: {"a": {1}, "b": {0}},
            1: {"a": {1}, "b": {0}},
        },
        start=0,
        accepting={1},
    )


def _epsilon_to_single_a() -> FSM:
    return FSM(
        states={0, 1, 2},
        alphabet={"a"},
        transitions={
            0: {EPSILON: {1}},
            1: {"a": {2}},
        },
        start=0,
        accepting={2},
    )


def _nondeterministic_no_epsilon() -> FSM:
    return FSM(
        states={0, 1, 2},
        alphabet={"a"},
        transitions={0: {"a": {1, 2}}},
        start=0,
        accepting={1, 2},
    )


def test_dfa_accepts_strings_ending_in_a():
    fsm = _ends_in_a()
    assert fsm.accepts("a")
    assert fsm.accepts("ba")
    assert fsm.accepts("bbbba")
    assert not fsm.accepts("")
    assert not fsm.accepts("ab")
    assert not fsm.accepts("b")


def test_dfa_is_deterministic_and_epsilon_free():
    fsm = _ends_in_a()
    assert fsm.is_deterministic
    assert fsm.is_epsilon_free


def test_epsilon_nfa_accepts_via_closure():
    fsm = _epsilon_to_single_a()
    assert fsm.accepts("a")
    assert not fsm.accepts("")
    assert not fsm.accepts("aa")


def test_epsilon_nfa_is_not_deterministic_or_epsilon_free():
    fsm = _epsilon_to_single_a()
    assert not fsm.is_epsilon_free
    assert not fsm.is_deterministic


def test_nondeterministic_without_epsilon():
    fsm = _nondeterministic_no_epsilon()
    assert fsm.is_epsilon_free
    assert not fsm.is_deterministic
    assert fsm.accepts("a")
    assert not fsm.accepts("")
    assert not fsm.accepts("aa")


def test_dead_end_short_circuits_accepts():
    fsm = FSM(
        states={0, 1},
        alphabet={"a"},
        transitions={0: {"a": {1}}},
        start=0,
        accepting={1},
    )
    assert not fsm.accepts("aa")  # no transition out of 1 on 'a'


def test_fields_are_normalized_to_frozensets():
    fsm = FSM(
        states=[0, 1],
        alphabet=["a"],
        transitions={0: {"a": [1]}},
        start=0,
        accepting=[1],
    )
    assert isinstance(fsm.states, frozenset)
    assert isinstance(fsm.alphabet, frozenset)
    assert isinstance(fsm.accepting, frozenset)
    assert isinstance(fsm.transitions[0]["a"], frozenset)


def test_equality_is_structural():
    assert _ends_in_a() == _ends_in_a()


def test_start_not_in_states_raises():
    with pytest.raises(ValueError, match="start state"):
        FSM(states={0}, alphabet=set(), transitions={}, start=1, accepting=set())


def test_accepting_not_subset_of_states_raises():
    with pytest.raises(ValueError, match="accepting states"):
        FSM(states={0}, alphabet=set(), transitions={}, start=0, accepting={1})


def test_transition_source_not_in_states_raises():
    with pytest.raises(ValueError, match="transition source state"):
        FSM(states={0}, alphabet={"a"}, transitions={1: {"a": {0}}}, start=0, accepting=set())


def test_transition_symbol_not_in_alphabet_raises():
    with pytest.raises(ValueError, match="transition symbol"):
        FSM(states={0}, alphabet=set(), transitions={0: {"a": {0}}}, start=0, accepting=set())


def test_transition_target_not_in_states_raises():
    with pytest.raises(ValueError, match="transition targets"):
        FSM(states={0}, alphabet={"a"}, transitions={0: {"a": {5}}}, start=0, accepting=set())
