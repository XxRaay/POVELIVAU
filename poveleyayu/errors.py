class PovelError(Exception):
    """Базовая ошибка языка ПОВЕЛЕВАЮ."""


class LexerError(PovelError):
    def __init__(self, line: int, char: str):
        super().__init__(
            f"Лихо стряслось при чтении свитка! Строка {line}: неведомый знак '{char}'"
        )


class ParseError(PovelError):
    def __init__(self, line: int, expected: str, got: str):
        super().__init__(
            f"Свиток составлен неверно! Строка {line}: ожидалось '{expected}', а явилось '{got}'"
        )


class RuntimeError(PovelError):
    @classmethod
    def undefined_name(cls, name: str):
        return cls(f"Беда в исполнении! Переменная '{name}' не была наречена!")

    @classmethod
    def division_by_zero(cls):
        return cls("Беда в исполнении! Нельзя разделить на нуль — сие противно природе!")
