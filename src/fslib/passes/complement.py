from fslib.fsm import FSM

from .determinize import determinize


def complement(fsm: FSM) -> FSM:
    if not fsm.is_deterministic or not _is_complete(fsm):
        fsm = determinize(fsm)

    return FSM(
        states=fsm.states,
        alphabet=fsm.alphabet,
        transitions=fsm.transitions,
        start=fsm.start,
        accepting=frozenset(fsm.states - fsm.accepting),
    )


def _is_complete(fsm: FSM) -> bool:
    return all(
        len(fsm.transitions.get(state, {}).get(symbol, ())) == 1 for state in fsm.states for symbol in fsm.alphabet
    )
