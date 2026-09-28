import fire

from .regex.parser import parse as parse_regex


class FslibCLI:
    def parse(self, regex: str) -> str:
        return repr(parse_regex(regex))


def main() -> None:
    fire.Fire(FslibCLI)


if __name__ == "__main__":
    main()
