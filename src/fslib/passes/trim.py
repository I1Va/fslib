from fslib.fsm import EPSILON, FSM, State, Symbol


def trim(fsm: FSM) -> FSM:
    states: set[State] = set(fsm.states)
    transitions: dict[State, dict[Symbol | None, set[State]]] = {
        state: {symbol: set(targets) for symbol, targets in edges.items()}
        for state, edges in fsm.transitions.items()
    }
    accepting: set[State] = set(fsm.accepting)
    start = fsm.start

    def out_degree(state: State) -> int:
        return sum(len(targets) for targets in transitions.get(state, {}).values())

    def predecessors() -> dict[State, list[tuple[State, Symbol | None]]]:
        preds: dict[State, list[tuple[State, Symbol | None]]] = {state: [] for state in states}
        for src, edges in transitions.items():
            for symbol, targets in edges.items():
                for dst in targets:
                    preds[dst].append((src, symbol))
        return preds

    def discard_edge(src: State, symbol: Symbol | None, dst: State) -> None:
        transitions[src][symbol].discard(dst)
        if not transitions[src][symbol]:
            del transitions[src][symbol]
        if not transitions[src]:
            del transitions[src]

    changed = True
    while changed:
        changed = False
        preds = predecessors()
        for u in states:
            for v in list(transitions.get(u, {}).get(EPSILON, ())):
                if v == u:
                    continue
                if v != start and preds[v] == [(u, EPSILON)]:
                    discard_edge(u, EPSILON, v)
                    for symbol, targets in transitions.pop(v, {}).items():
                        transitions.setdefault(u, {}).setdefault(symbol, set()).update(targets)
                    if v in accepting:
                        accepting.discard(v)
                        accepting.add(u)
                    states.discard(v)
                    changed = True
                    break
                if u not in accepting and out_degree(u) == 1:
                    for src, symbol in preds[u]:
                        if src == u:
                            continue
                        discard_edge(src, symbol, u)
                        transitions.setdefault(src, {}).setdefault(symbol, set()).add(v)
                    transitions.pop(u, None)
                    if u == start:
                        start = v
                    states.discard(u)
                    changed = True
                    break
            if changed:
                break

    renumber = {state: i for i, state in enumerate(sorted(states))}
    return FSM(
        states=frozenset(renumber.values()),
        alphabet=fsm.alphabet,
        transitions={
            renumber[state]: {symbol: frozenset(renumber[t] for t in targets) for symbol, targets in edges.items()}
            for state, edges in transitions.items()
        },
        start=renumber[start],
        accepting=frozenset(renumber[state] for state in accepting),
    )
