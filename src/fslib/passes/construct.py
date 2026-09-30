import itertools
from collections import defaultdict

from fslib.fsm import FSM, State, Symbol
from fslib.regex.ast import RegexNode

from .trim import trim


def thompson(ast: RegexNode) -> FSM:
    alphabet = ast.literals()
    builder = _Builder(alphabet)
    start, accept = ast.build(builder)
    fsm = FSM(
        states=frozenset(builder.states),
        alphabet=alphabet,
        transitions=builder.transitions,
        start=start,
        accepting=frozenset({accept}),
    )
    return trim(fsm)


class _Builder:
    def __init__(self, alphabet: frozenset[Symbol]) -> None:
        self.alphabet = alphabet
        self._counter = itertools.count()
        self.states: set[State] = set()
        self.transitions: dict[State, dict[Symbol | None, set[State]]] = defaultdict(lambda: defaultdict(set))

    def new_state(self) -> State:
        state = next(self._counter)
        self.states.add(state)
        return state

    def add_edge(self, src: State, symbol: Symbol | None, dst: State) -> None:
        self.transitions[src][symbol].add(dst)
