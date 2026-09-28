from collections import defaultdict

from fslib.fsm import FSM, State, Symbol


def minimize(dfa: FSM) -> FSM:
    if not dfa.is_deterministic:
        raise ValueError("minimize requires a deterministic FSM; call determinize() first")
    if not _is_complete(dfa):
        raise ValueError("minimize requires a complete FSM (missing transitions); call determinize() first")

    reachable = _reachable_states(dfa)
    accepting = dfa.accepting & reachable
    non_accepting = reachable - accepting

    partition: list[frozenset[State]] = [block for block in (accepting, non_accepting) if block]
    worklist: list[frozenset[State]] = list(partition)

    predecessors: dict[tuple[Symbol, State], set[State]] = defaultdict(set)
    for src in reachable:
        for symbol, targets in dfa.transitions.get(src, {}).items():
            for dst in targets:
                predecessors[(symbol, dst)].add(src)

    while worklist:
        splitter = worklist.pop()
        for symbol in dfa.alphabet:
            sources: set[State] = set()
            for state in splitter:
                sources |= predecessors.get((symbol, state), set())
            if not sources:
                continue
            new_partition = []
            for block in partition:
                intersection = block & sources
                difference = block - sources
                if intersection and difference:
                    new_partition.append(intersection)
                    new_partition.append(difference)
                    if block in worklist:
                        worklist.remove(block)
                        worklist.append(intersection)
                        worklist.append(difference)
                    elif len(intersection) <= len(difference):
                        worklist.append(intersection)
                    else:
                        worklist.append(difference)
                else:
                    new_partition.append(block)
            partition = new_partition

    block_id = {state: i for i, block in enumerate(partition) for state in block}
    transitions: dict[State, dict[Symbol, frozenset[State]]] = {}
    for i, block in enumerate(partition):
        representative = next(iter(block))
        edges = dfa.transitions.get(representative, {})
        transitions[i] = {symbol: frozenset({block_id[next(iter(targets))]}) for symbol, targets in edges.items()}

    return FSM(
        states=frozenset(range(len(partition))),
        alphabet=dfa.alphabet,
        transitions=transitions,
        start=block_id[dfa.start],
        accepting=frozenset(i for i, block in enumerate(partition) if block & dfa.accepting),
    )


def _reachable_states(dfa: FSM) -> frozenset[State]:
    seen = {dfa.start}
    stack = [dfa.start]
    while stack:
        state = stack.pop()
        for targets in dfa.transitions.get(state, {}).values():
            for target in targets:
                if target not in seen:
                    seen.add(target)
                    stack.append(target)
    return frozenset(seen)


def _is_complete(dfa: FSM) -> bool:
    return all(
        len(dfa.transitions.get(state, {}).get(symbol, ())) == 1 for state in dfa.states for symbol in dfa.alphabet
    )
