import fire

from .regex.parser import parse as parse_regex
from .viz import ast_to_dot, render


class FslibCLI:
    def parse(self, regex: str) -> str:
        return repr(parse_regex(regex))

    def tree(self, regex: str, out: str | None = None) -> str:
        dot_source = ast_to_dot(parse_regex(regex))
        if out is None:
            return dot_source
        if out.endswith(".dot"):
            with open(out, "w") as f:
                f.write(dot_source)
        else:
            render(dot_source, out)
        return f"wrote {out}"


def main() -> None:
    fire.Fire(FslibCLI)


if __name__ == "__main__":
    main()
