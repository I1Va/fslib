import fire

from .passes.complement import complement
from .passes.construct import thompson
from .passes.determinize import determinize
from .passes.minimize import minimize
from .passes.to_regex import fsm_to_regex
from .regex.parser import parse as parse_regex
from .viz import ast_to_dot, fsm_to_dot, render


def _nfa(regex: str, alphabet: str | None):
    return thompson(parse_regex(regex), frozenset(str(alphabet)) if alphabet else None)


def _emit(dot_source: str, out: str | None) -> str:
    if out is None:
        return dot_source
    if out.endswith(".dot"):
        with open(out, "w") as f:
            f.write(dot_source)
    else:
        render(dot_source, out)
    return f"wrote {out}"


class FslibCLI:
    def parse(self, regex: str) -> str:
        return repr(parse_regex(regex))

    def tree(self, regex: str, out: str | None = None) -> str:
        return _emit(ast_to_dot(parse_regex(regex)), out)

    def automaton(self, regex: str, out: str | None = None, alphabet: str | None = None) -> str:
        return _emit(fsm_to_dot(_nfa(regex, alphabet)), out)

    def dfa(self, regex: str, out: str | None = None, alphabet: str | None = None) -> str:
        return _emit(fsm_to_dot(determinize(_nfa(regex, alphabet))), out)

    def min(self, regex: str, out: str | None = None, alphabet: str | None = None) -> str:
        return _emit(fsm_to_dot(minimize(determinize(_nfa(regex, alphabet)))), out)

    def complement(self, regex: str, out: str | None = None, alphabet: str | None = None) -> str:
        fsm = complement(minimize(determinize(_nfa(regex, alphabet))))
        return _emit(fsm_to_dot(fsm), out)

    def regex(self, regex: str, alphabet: str | None = None) -> str:
        return fsm_to_regex(minimize(determinize(_nfa(regex, alphabet)))).pattern()

    def complement_regex(self, regex: str, alphabet: str | None = None) -> str:
        fsm = complement(minimize(determinize(_nfa(regex, alphabet))))
        return fsm_to_regex(minimize(fsm)).pattern()

    def match(self, regex: str, word: str, alphabet: str | None = None) -> bool:
        return minimize(determinize(_nfa(regex, alphabet))).accepts(word)


def main() -> None:
    fire.Fire(FslibCLI)


if __name__ == "__main__":
    main()
