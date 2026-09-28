from collections import deque

from fslib.fsm import FSM, State, Symbol


def determinize(nfa: FSM) -> FSM:
    initial = nfa.epsilon_closure(frozenset({nfa.start}))
    ids: dict[frozenset[State], State] = {initial: 0}
    transitions: dict[State, dict[Symbol, frozenset[State]]] = {}

    queue: deque[frozenset[State]] = deque([initial])
    while queue:
        current = queue.popleft()
        current_id = ids[current]
        transitions[current_id] = {}
        for symbol in sorted(nfa.alphabet):
            moved: set[State] = set()
            for state in current:
                moved.update(nfa.transitions.get(state, {}).get(symbol, ()))
            target = nfa.epsilon_closure(frozenset(moved))
            if target not in ids:
                ids[target] = len(ids)
                queue.append(target)
            transitions[current_id][symbol] = frozenset({ids[target]})

    accepting = frozenset(state_id for subset, state_id in ids.items() if subset & nfa.accepting)

    return FSM(
        states=frozenset(ids.values()),
        alphabet=nfa.alphabet,
        transitions=transitions,
        start=ids[initial],
        accepting=accepting,
    )
