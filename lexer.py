# lexer.py — Лексер языка ПОВЕЛЕВАЮ
import re
from dataclasses import dataclass
from typing import List, Optional
from errors import LexerError


# ─────────────────────────── Типы токенов ────────────────────────────
class TT:
    # Структурные
    NEWLINE      = 'NEWLINE'
    INDENT       = 'INDENT'
    DEDENT       = 'DEDENT'
    COMMA        = 'COMMA'
    COLON        = 'COLON'
    LPAREN       = 'LPAREN'
    RPAREN       = 'RPAREN'
    LBRACKET     = 'LBRACKET'
    RBRACKET     = 'RBRACKET'
    EOF          = 'EOF'
    # Литералы
    NUMBER       = 'NUMBER'
    STRING       = 'STRING'
    BOOL_TRUE    = 'BOOL_TRUE'
    BOOL_FALSE   = 'BOOL_FALSE'
    NONE         = 'NONE'
    # Идентификатор (имя переменной / слово)
    IDENT        = 'IDENT'
    # Ключевые слова (многословные — объединяем)
    KW           = 'KW'


@dataclass
class Token:
    type: str
    value: str
    line: int

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, ln={self.line})"


# ─────────────────────────── Лексер ──────────────────────────────────
class Lexer:
    """
    Разбивает исходный текст программы на Повелеваю на список токенов.
    Многословные ключевые слова склеиваются в один токен KW.
    Отступы порождают INDENT/DEDENT.
    """

    # Все многословные ключевые слова (от длинных к коротким!)
    KEYWORDS = [
        # Заголовок
        "Свиток",
        # Присвоение
        "Повелеваю: Отныне",
        "Указываю: Сотворить сундук пустой, именем",
        "и положить в него",
        "именоваться",
        # Вывод
        "Глаголю народу:",
        "Вещаю:",
        "Вещаю построчно:",
        "Кричу на всю Русь:",
        # Ввод
        "Повелеваю: Взять слово от гостя заезжего, оборотить его в Число Цельное и наречь",
        "Повелеваю: Взять слово от гостя заезжего, оборотить его в Число Дробное и наречь",
        "Повелеваю: Взять слово от гостя заезжего и наречь",
        "Вопрошаю гостя:",
        "и наречь",
        # Условия
        "Суд вершу:",
        "Коль",
        "Иначе коль",
        "Иначе:",
        # Циклы
        "Коловрат покуда",
        "Коловрат:",
        "Коловрат",
        "Повелеваю: Пресечь бег сего коловрата",
        "Повелеваю: Перейти к следующему витку",
        # For
        "Странствие",
        "по землям от",
        "по дружине",
        "до",
        # Функции
        "Умение нарекаю",
        "Призвать умение",
        "Повелеваю: Вернуть",
        # Списки
        "Дружина именем",
        "с ратниками",
        "Принять в дружину",
        "ратника",
        "Изгнать из дружины",
        "ратника с позиции",
        "Ратник под номером",
        "в дружине",
        "длина дружины",
        # Математика
        "сложить с",
        "отнять",
        "умножить на",
        "разделить на",
        "остаток от деления на",
        "Добавить в сундук",
        "единицу малую",
        "единицу",
        "Убавить из сундука",
        # Каст
        "оборотить его в Число Цельное",
        "оборотить его в Число Дробное",
        "оборотить его в Слово",
        "оборотить",
        "в Число Цельное",
        "в Число Дробное",
        "в Слово",
        # Стандартная библиотека / сеть / случайное
        "из земель дальних послать весть по адресу",
        "из земель дальних призвать весть по адресу",
        "с содержимым",
        "из палат случайных призвать число от",
        # Файловая система — Устав Управления Землями
        "Повелеваю: Обозреть всё в пределе текущем и наречь",
        "Повелеваю: Узнать имя земли текущей и наречь",
        "Повелеваю: Сменить землю на",
        "и обосноваться там",
        "Повелеваю: Возвести чертог новый именем",
        "Повелеваю: Предать забвению чертог",
        "со всеми свитками",
        "Повелеваю: Изгнать из земель свиток",
        "Повелеваю: Переименовать грамоту",
        "Повелеваю: Сотворить свиток",
        "в землях есть",
        "Повелеваю: Вписать в свиток",
        # TXT-свитки: чтение и вычёркивание строки
        "прочитать свиток",
        "Повелеваю: Вычеркнуть из свитка",
        "строку под номером",
        "строку",
        # Булевы
        "Зрю истину",
        "Зрю ложь",
        "ничто",
        # Спец-литералы
        "перенос строки",
        # Операторы сравнения
        "в точности как",
        "не ровня",
        "не меньше",
        "не больше",
        "меньше",
        "больше",
        # Логические
        "и к тому же",
        "либо же",
        "не есть",
        # Спец
        "Повелеваю: Остановить всё и почить",
        "Повелеваю: Начать выполнение!",
        # Разное
        "по",
        "именем",
    ]

    def __init__(self, source: str):
        self.source = source
        self.lines = source.split('\n')
        self.tokens: List[Token] = []
        self.pos = 0
        self.line = 1

    # ── Главный метод ──────────────────────────────────────────────
    def tokenize(self) -> List[Token]:
        indent_stack = [0]

        for lineno, raw_line in enumerate(self.lines, 1):
            self.line = lineno

            # Убираем только правые пробелы (не левые — там отступы)
            line = raw_line.rstrip()

            # Пустая строка
            if not line.strip():
                continue

            # Комментарий
            if line.lstrip().startswith('//'):
                continue

            # Считаем отступ
            stripped = line.lstrip(' \t')
            indent_chars = len(line) - len(stripped)
            # Нормализуем таб → 5 пробелов
            leading = line[:len(line) - len(stripped)]
            indent = leading.count('\t') * 5 + leading.count(' ')

            # INDENT / DEDENT
            current_indent = indent_stack[-1]
            if indent > current_indent:
                indent_stack.append(indent)
                self.tokens.append(Token(TT.INDENT, '', lineno))
            elif indent < current_indent:
                while indent_stack and indent_stack[-1] > indent:
                    indent_stack.pop()
                    self.tokens.append(Token(TT.DEDENT, '', lineno))

            # Токенизируем содержимое строки
            self._tokenize_line(stripped, lineno)
            self.tokens.append(Token(TT.NEWLINE, '', lineno))

        # Закрываем все отступы
        while len(indent_stack) > 1:
            indent_stack.pop()
            self.tokens.append(Token(TT.DEDENT, '', self.line))

        self.tokens.append(Token(TT.EOF, '', self.line))
        return self.tokens

    # ── Токенизация одной строки ────────────────────────────────────
    def _tokenize_line(self, text: str, lineno: int):
        pos = 0
        while pos < len(text):
            # Пропуск пробелов
            if text[pos] in ' \t':
                pos += 1
                continue

            # Комментарий
            if text[pos:pos+2] == '//':
                break

            # Строка
            if text[pos] == '"':
                end = text.find('"', pos + 1)
                if end == -1:
                    raise LexerError(lineno, text[pos])
                self.tokens.append(Token(TT.STRING, text[pos+1:end], lineno))
                pos = end + 1
                continue

            # Запятая (только если НЕ внутри многословного ключевого слова)
            if text[pos] == ',':
                self.tokens.append(Token(TT.COMMA, ',', lineno))
                pos += 1
                continue

            if text[pos] == ':':
                self.tokens.append(Token(TT.COLON, ':', lineno))
                pos += 1
                continue

            if text[pos] == '(':
                self.tokens.append(Token(TT.LPAREN, '(', lineno))
                pos += 1
                continue

            if text[pos] == ')':
                self.tokens.append(Token(TT.RPAREN, ')', lineno))
                pos += 1
                continue

            if text[pos] == '[':
                self.tokens.append(Token(TT.LBRACKET, '[', lineno))
                pos += 1
                continue

            if text[pos] == ']':
                self.tokens.append(Token(TT.RBRACKET, ']', lineno))
                pos += 1
                continue

            # Число
            m = re.match(r'\d+(\.\d+)?', text[pos:])
            if m:
                self.tokens.append(Token(TT.NUMBER, m.group(), lineno))
                pos += m.end()
                continue

            # Многословные ключевые слова (пробуем от длинных к коротким)
            matched = False
            for kw in self.KEYWORDS:
                if text[pos:].startswith(kw):
                    # Проверяем, что после ключевого слова идёт не буква/цифра
                    end_pos = pos + len(kw)
                    if end_pos < len(text) and (text[end_pos].isalnum() or text[end_pos] in '_'):
                        # Может быть префикс другого слова — пропускаем
                        pass
                    else:
                        self.tokens.append(Token(TT.KW, kw, lineno))
                        pos = end_pos
                        matched = True
                        break
            if matched:
                continue

            # Идентификатор (кириллица или латиница)
            m = re.match(r'[А-ЯЁа-яёA-Za-z_][А-ЯЁа-яёA-Za-z0-9_]*', text[pos:])
            if m:
                word = m.group()
                self.tokens.append(Token(TT.IDENT, word, lineno))
                pos += m.end()
                continue

            # Восклицательный знак (конец программы)
            if text[pos] == '!':
                pos += 1
                continue

            raise LexerError(lineno, text[pos])
