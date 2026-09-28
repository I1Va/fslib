from dataclasses import dataclass

Symbol = str
State = int
EPSILON = None


@dataclass(frozen=True)
class FSM:
    states: frozenset[State]
    alphabet: frozenset[Symbol]
    transitions: dict[State, dict[Symbol | None, frozenset[State]]]
    start: State
    accepting: frozenset[State]

    def __post_init__(self) -> None:
        states = frozenset(self.states)
        alphabet = frozenset(self.alphabet)
        transitions = {
            state: {symbol: frozenset(targets) for symbol, targets in edges.items()}
            for state, edges in self.transitions.items()
        }
        accepting = frozenset(self.accepting)
        object.__setattr__(self, "states", states)
        object.__setattr__(self, "alphabet", alphabet)
        object.__setattr__(self, "transitions", transitions)
        object.__setattr__(self, "accepting", accepting)

        if self.start not in states:
            raise ValueError(f"start state {self.start!r} is not in states")
        if not accepting <= states:
            raise ValueError(f"accepting states {accepting - states} are not in states")
        for state, edges in transitions.items():
            if state not in states:
                raise ValueError(f"transition source state {state!r} is not in states")
            for symbol, targets in edges.items():
                if symbol is not None and symbol not in alphabet:
                    raise ValueError(f"transition symbol {symbol!r} is not in alphabet")
                if not targets <= states:
                    raise ValueError(f"transition targets {targets - states} are not in states")

    @property
    def is_epsilon_free(self) -> bool:
        return all(EPSILON not in edges for edges in self.transitions.values())

    @property
    def is_deterministic(self) -> bool:
        if not self.is_epsilon_free:
            return False
        return all(len(targets) <= 1 for edges in self.transitions.values() for targets in edges.values())

    def _epsilon_closure(self, states: frozenset[State]) -> frozenset[State]:
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for target in self.transitions.get(state, {}).get(EPSILON, ()):
                if target not in closure:
                    closure.add(target)
                    stack.append(target)
        return frozenset(closure)

    def accepts(self, word: str) -> bool:
        current = self._epsilon_closure(frozenset({self.start}))
        for symbol in word:
            next_states: set[State] = set()
            for state in current:
                next_states.update(self.transitions.get(state, {}).get(symbol, ()))
            if not next_states:
                return False
            current = self._epsilon_closure(frozenset(next_states))
        return bool(current & self.accepting)
