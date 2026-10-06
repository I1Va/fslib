from fslib.fsm import EPSILON, FSM, State
from fslib.regex.ast import Concat, Epsilon, Literal, RegexNode, Star, Union

_EMPTY = None
_Label = RegexNode | None


def fsm_to_regex(fsm: FSM) -> RegexNode:
    live = _live_states(fsm)
    if fsm.start not in live:
        raise ValueError("language is empty; this syntax has no notation for the empty set")

    start, end = -1, -2
    labels: dict[tuple[State, State], _Label] = {}

    def add(src: State, dst: State, label: _Label) -> None:
        labels[(src, dst)] = _union(labels.get((src, dst)), label)

    for src, edges in fsm.transitions.items():
        if src not in live:
            continue
        for symbol, targets in edges.items():
            label = Epsilon() if symbol is EPSILON else Literal(symbol)
            for dst in targets:
                if dst in live:
                    add(src, dst, label)

    add(start, fsm.start, Epsilon())
    for state in sorted(fsm.accepting & live):
        add(state, end, Epsilon())

    remaining = set(live)
    while remaining:
        state = min(remaining, key=lambda s: _weight(s, labels))
        remaining.discard(state)
        loop = _star(labels.pop((state, state), _EMPTY))
        incoming = [(p, lab) for (p, q), lab in labels.items() if q == state]
        outgoing = [(q, lab) for (p, q), lab in labels.items() if p == state]
        for p, before in incoming:
            for q, after in outgoing:
                add(p, q, _concat(_concat(before, loop), after))
        for key in [k for k in labels if state in k]:
            del labels[key]

    answer = labels.get((start, end), _EMPTY)
    if answer is _EMPTY:
        raise ValueError("language is empty; this syntax has no notation for the empty set")
    return answer


def _live_states(fsm: FSM) -> frozenset[State]:
    reachable = {fsm.start}
    stack = [fsm.start]
    while stack:
        state = stack.pop()
        for targets in fsm.transitions.get(state, {}).values():
            for target in targets:
                if target not in reachable:
                    reachable.add(target)
                    stack.append(target)

    backwards: dict[State, set[State]] = {}
    for src, edges in fsm.transitions.items():
        for targets in edges.values():
            for dst in targets:
                backwards.setdefault(dst, set()).add(src)

    productive = set(fsm.accepting)
    stack = list(productive)
    while stack:
        state = stack.pop()
        for pred in backwards.get(state, ()):
            if pred not in productive:
                productive.add(pred)
                stack.append(pred)

    return frozenset(reachable & productive)


def _weight(state: State, labels: dict[tuple[State, State], _Label]) -> int:
    incoming = sum(1 for (p, q) in labels if q == state and p != state)
    outgoing = sum(1 for (p, q) in labels if p == state and q != state)
    return incoming * outgoing


def _union(left: _Label, right: _Label) -> _Label:
    if left is _EMPTY:
        return right
    if right is _EMPTY or left == right:
        return left
    return Union(left, right)


def _concat(left: _Label, right: _Label) -> _Label:
    if left is _EMPTY or right is _EMPTY:
        return _EMPTY
    if left == Epsilon():
        return right
    if right == Epsilon():
        return left
    return Concat(left, right)


def _star(label: _Label) -> _Label:
    if label is _EMPTY or label == Epsilon():
        return Epsilon()
    if isinstance(label, Star):
        return label
    return Star(label)
