from fslib.fsm import FSM


def complement(dfa: FSM) -> FSM:
    if not dfa.is_deterministic:
        raise ValueError("complement requires a deterministic FSM; call determinize() first")
    if not _is_complete(dfa):
        raise ValueError("complement requires a complete FSM; call determinize() first")

    return FSM(
        states=dfa.states,
        alphabet=dfa.alphabet,
        transitions=dfa.transitions,
        start=dfa.start,
        accepting=frozenset(dfa.states - dfa.accepting),
    )


def _is_complete(dfa: FSM) -> bool:
    return all(
        len(dfa.transitions.get(state, {}).get(symbol, ())) == 1 for state in dfa.states for symbol in dfa.alphabet
    )
