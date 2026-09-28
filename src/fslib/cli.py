import fire

from .passes.construct import thompson
from .regex.parser import parse as parse_regex
from .viz import ast_to_dot, fsm_to_dot, render


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

    def automaton(self, regex: str, out: str | None = None) -> str:
        fsm = thompson(parse_regex(regex))
        return _emit(fsm_to_dot(fsm), out)


def main() -> None:
    fire.Fire(FslibCLI)


if __name__ == "__main__":
    main()
