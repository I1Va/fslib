class RegexSyntaxError(ValueError):
    def __init__(self, message: str, pattern: str, position: int) -> None:
        self.message = message
        self.pattern = pattern
        self.position = position
        super().__init__(str(self))

    def __str__(self) -> str:
        caret_line = " " * self.position + "^"
        return f"{self.message}\n{self.pattern}\n{caret_line}"
