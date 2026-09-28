import itertools
from collections import defaultdict

from fslib.fsm import EPSILON, FSM, State, Symbol
from fslib.regex.ast import Concat, Epsilon, Literal, Plus, RegexNode, Star, Union, Wildcard


def thompson(ast: RegexNode) -> FSM:
    alphabet = _collect_alphabet(ast)
    builder = _Builder(alphabet)
    start, accept = builder.build(ast)
    return FSM(
        states=frozenset(builder.states),
        alphabet=alphabet,
        transitions=builder.transitions,
        start=start,
        accepting=frozenset({accept}),
    )


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

    def build(self, node: RegexNode) -> tuple[State, State]:
        if isinstance(node, Literal):
            return self._build_symbol(node.char)
        if isinstance(node, Epsilon):
            return self._build_epsilon()
        if isinstance(node, Wildcard):
            return self._build_wildcard()
        if isinstance(node, Concat):
            return self._build_concat(node)
        if isinstance(node, Union):
            return self._build_union(node)
        if isinstance(node, Star):
            return self._build_star(node)
        if isinstance(node, Plus):
            return self._build_plus(node)
        raise TypeError(f"unknown AST node type: {type(node).__name__}")

    def _build_epsilon(self) -> tuple[State, State]:
        start, accept = self.new_state(), self.new_state()
        self.add_edge(start, EPSILON, accept)
        return start, accept

    def _build_symbol(self, char: Symbol) -> tuple[State, State]:
        start, accept = self.new_state(), self.new_state()
        self.add_edge(start, char, accept)
        return start, accept

    def _build_wildcard(self) -> tuple[State, State]:
        start, accept = self.new_state(), self.new_state()
        for symbol in self.alphabet:
            self.add_edge(start, symbol, accept)
        return start, accept

    def _build_concat(self, node: Concat) -> tuple[State, State]:
        start1, accept1 = self.build(node.left)
        start2, accept2 = self.build(node.right)
        self.add_edge(accept1, EPSILON, start2)
        return start1, accept2

    def _build_union(self, node: Union) -> tuple[State, State]:
        start1, accept1 = self.build(node.left)
        start2, accept2 = self.build(node.right)
        start, accept = self.new_state(), self.new_state()
        self.add_edge(start, EPSILON, start1)
        self.add_edge(start, EPSILON, start2)
        self.add_edge(accept1, EPSILON, accept)
        self.add_edge(accept2, EPSILON, accept)
        return start, accept

    def _build_star(self, node: Star) -> tuple[State, State]:
        inner_start, inner_accept = self.build(node.child)
        start, accept = self.new_state(), self.new_state()
        self.add_edge(start, EPSILON, inner_start)
        self.add_edge(start, EPSILON, accept)
        self.add_edge(inner_accept, EPSILON, inner_start)
        self.add_edge(inner_accept, EPSILON, accept)
        return start, accept

    def _build_plus(self, node: Plus) -> tuple[State, State]:
        start, accept = self.build(node.child)
        self.add_edge(accept, EPSILON, start)
        return start, accept


def _collect_alphabet(node: RegexNode) -> frozenset[Symbol]:
    if isinstance(node, Literal):
        return frozenset({node.char})
    if isinstance(node, (Concat, Union)):
        return _collect_alphabet(node.left) | _collect_alphabet(node.right)
    if isinstance(node, (Star, Plus)):
        return _collect_alphabet(node.child)
    return frozenset()
