import itertools

from fslib.fsm import FSM

finite = FSM(states={0, 1, 2}, alphabet={"a", "b"}, transitions={0: {"a": {1}}, 1: {"b": {2}}}, start=0, accepting={2})
infinite = FSM(
    states={0, 1, 2},
    alphabet={"a", "b"},
    transitions={0: {"a": {1}}, 1: {"b": {2}}, 2: {"a": {1}}},
    start=0,
    accepting={1},
)


def is_infinite(f, n, alphabet):
    for k in range(n, 2 * n):
        for word in itertools.product(alphabet, repeat=k):
            if f("".join(word)):
                return True
    return False


for name, fsm in [("finite {ab}", finite), ("infinite a(ba)*", infinite)]:
    print(name, "->", is_infinite(fsm.accepts, len(fsm.states), sorted(fsm.alphabet)))
