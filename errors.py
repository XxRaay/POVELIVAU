# errors.py — Ошибки языка ПОВЕЛЕВАЮ на древнерусский манер


class PovelError(Exception):
    """Базовый класс ошибок языка Повелеваю"""
    pass


class LexerError(PovelError):
    def __init__(self, line: int, char: str):
        msg = (
            f"⚔ Лихо стряслось при чтении свитка!\n"
            f"  Строка {line}: неведомый знак '{char}'"
        )
        super().__init__(msg)


class ParseError(PovelError):
    def __init__(self, line: int, message: str, expected: str = None, got: str = None):
        # Если передали expected/got — формируем человекочитаемое описание.
        if expected is not None and got is not None:
            shown_got = got if got else "иное"
            detail = f"ожидалось '{expected}', а явилось '{shown_got}'"
        else:
            # Если message пустой — даём общее описание, чтобы не было "пустой" ошибки
            detail = message or "свиток составлен неверно (синтаксическая ошибка)"
        msg = (
            f"⚔ Свиток составлен неверно!\n"
            f"  Строка {line}: {detail}"
        )
        super().__init__(msg)


class PovelRuntimeError(PovelError):
    def __init__(self, message: str):
        msg = f"⚔ Беда в исполнении!\n  {message}"
        super().__init__(msg)


class UndefinedVariableError(PovelRuntimeError):
    def __init__(self, name: str):
        super().__init__(f"Переменная '{name}' не была наречена!")


class DivisionByZeroError(PovelRuntimeError):
    def __init__(self):
        super().__init__("Нельзя разделить на нуль — сие противно природе!")


class TypePovelError(PovelRuntimeError):
    def __init__(self, detail: str):
        super().__init__(f"Непотребное смешение родов: {detail}")


class ReturnSignal(Exception):
    """Внутренний сигнал возврата из функции"""
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    """Внутренний сигнал прерывания цикла"""
    pass


class ContinueSignal(Exception):
    """Внутренний сигнал перехода к следующей итерации"""
    pass
