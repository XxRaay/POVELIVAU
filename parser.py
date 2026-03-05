# parser.py — Рекурсивный нисходящий парсер языка ПОВЕЛЕВАЮ
from typing import List, Optional
from lexer import Token, TT
from nodes import *
from errors import ParseError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TT.NEWLINE or True]
        # Фильтруем лишние NEWLINE между INDENT/DEDENT для удобства
        self.tokens = self._clean_tokens(tokens)
        self.pos = 0

    def _clean_tokens(self, tokens):
        """Убираем подряд идущие NEWLINE и NEWLINE прямо перед DEDENT/INDENT"""
        result = []
        for tok in tokens:
            if tok.type == TT.NEWLINE:
                # пропускаем дублирующиеся NEWLINE
                if result and result[-1].type == TT.NEWLINE:
                    continue
                # пропускаем NEWLINE перед DEDENT/EOF
            result.append(tok)
        return result

    # ── Вспомогательные методы ──────────────────────────────────────
    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset=1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def skip_newlines(self):
        while self.current().type == TT.NEWLINE:
            self.advance()

    def expect_kw(self, kw: str) -> Token:
        tok = self.current()
        if tok.type != TT.KW or tok.value != kw:
            raise ParseError(tok.line, '', expected=kw, got=tok.value)
        return self.advance()

    def match_kw(self, *kws) -> Optional[Token]:
        tok = self.current()
        if tok.type == TT.KW and tok.value in kws:
            return self.advance()
        return None

    def match_type(self, *types) -> Optional[Token]:
        tok = self.current()
        if tok.type in types:
            return self.advance()
        return None

    def expect_type(self, *types) -> Token:
        tok = self.current()
        if tok.type not in types:
            raise ParseError(tok.line, '', expected=str(types), got=tok.value)
        return self.advance()

    def at_kw(self, *kws) -> bool:
        tok = self.current()
        return tok.type == TT.KW and tok.value in kws

    def at_type(self, *types) -> bool:
        return self.current().type in types

    # ── Парсинг программы ───────────────────────────────────────────
    def parse(self) -> ProgramNode:
        self.skip_newlines()
        line = self.current().line

        # Свиток <Тип> "<Название>" — обязателен
        scroll_type = 'Свитка'
        title = 'Без названия'
        if not self.at_kw('Свиток'):
            tok = self.current()
            raise ParseError(tok.line, "Ожидался заголовок 'Свиток <Тип> \"<Название>\"' в начале свитка")

        # Ключевое слово "Свиток"
        self.advance()

        # Не требуем тип и название строго, но если они есть — разбираем
        if self.at_type(TT.IDENT):
            scroll_type = self.advance().value
        if self.at_type(TT.STRING):
            title = self.advance().value

        self.skip_newlines()

        body = self.parse_block_or_top()

        # Обязательная команда запуска программы в конце
        if not self.match_kw('Повелеваю: Начать выполнение!'):
            tok = self.current()
            raise ParseError(tok.line, "Ожидалось 'Повелеваю: Начать выполнение!' в конце свитка")

        return ProgramNode(line=line, title=title, scroll_type=scroll_type, body=body)

    def parse_block_or_top(self) -> List[Node]:
        """Парсит список инструкций на текущем уровне вложенности"""
        stmts = []
        while True:
            self.skip_newlines()
            tok = self.current()
            if tok.type in (TT.EOF,):
                break
            if tok.type == TT.DEDENT:
                break
            if tok.type == TT.KW and tok.value == 'Повелеваю: Начать выполнение!':
                break

            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def parse_indented_block(self) -> List[Node]:
        """Парсит вложенный блок после INDENT"""
        self.skip_newlines()
        if self.at_type(TT.INDENT):
            self.advance()
        stmts = []
        while True:
            self.skip_newlines()
            if self.at_type(TT.DEDENT, TT.EOF):
                break
            if self.at_kw('Повелеваю: Начать выполнение!'):
                break
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
        if self.at_type(TT.DEDENT):
            self.advance()
        return stmts

    # ── Инструкции ──────────────────────────────────────────────────
    def parse_statement(self) -> Optional[Node]:
        tok = self.current()
        line = tok.line

        # Пропуск пустых строк
        if tok.type == TT.NEWLINE:
            self.advance()
            return None

        # ── Присвоение: Повелеваю: Отныне <expr> именоваться <Имя>
        if self.at_kw('Повелеваю: Отныне'):
            self.advance()
            value = self.parse_expression()
            self.expect_kw('именоваться')
            name = self.expect_type(TT.IDENT).value
            self.match_type(TT.COMMA)
            return AssignNode(line=line, name=name, value=value)

        # ── Присвоение: Указываю: Сотворить сундук пустой, именем <Имя>, и положить в него <expr>
        if self.at_kw('Указываю: Сотворить сундук пустой, именем'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            self.match_type(TT.COMMA)
            self.expect_kw('и положить в него')
            value = self.parse_expression()
            self.match_type(TT.COMMA)
            return AssignNode(line=line, name=name, value=value)

        # ── Вывод: Глаголю народу / Вещаю / Кричу на всю Русь
        if self.at_kw('Глаголю народу:', 'Вещаю:', 'Кричу на всю Русь:'):
            self.advance()
            value = self.parse_expression()
            self.match_type(TT.COMMA)
            return PrintNode(line=line, value=value)

        # ── Ввод с кастом: Взять слово ... в Число Цельное ... и наречь <Имя>
        if self.at_kw('Повелеваю: Взять слово от гостя заезжего, оборотить его в Число Цельное и наречь'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            self.match_type(TT.COMMA)
            return InputNode(line=line, name=name, cast='int')

        if self.at_kw('Повелеваю: Взять слово от гостя заезжего, оборотить его в Число Дробное и наречь'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            self.match_type(TT.COMMA)
            return InputNode(line=line, name=name, cast='float')

        # ── Ввод простой: Взять слово от гостя заезжего и наречь <Имя>
        if self.at_kw('Повелеваю: Взять слово от гостя заезжего и наречь'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            self.match_type(TT.COMMA)
            return InputNode(line=line, name=name)

        # ── Ввод с подсказкой: Вопрошаю гостя: "<подсказка>" и наречь <Имя>
        if self.at_kw('Вопрошаю гостя:'):
            self.advance()
            prompt = self.parse_expression()
            self.expect_kw('и наречь')
            name = self.expect_type(TT.IDENT).value
            self.match_type(TT.COMMA)
            return InputNode(line=line, name=name, prompt=prompt)

        # ── Break
        if self.at_kw('Повелеваю: Пресечь бег сего коловрата'):
            self.advance()
            self.match_type(TT.COMMA)
            return BreakNode(line=line)

        # ── Continue
        if self.at_kw('Повелеваю: Перейти к следующему витку'):
            self.advance()
            self.match_type(TT.COMMA)
            return ContinueNode(line=line)

        # ── Return
        if self.at_kw('Повелеваю: Вернуть'):
            self.advance()
            value = self.parse_expression()
            self.match_type(TT.COMMA)
            return ReturnNode(line=line, value=value)

        # ── Exit
        if self.at_kw('Повелеваю: Остановить всё и почить'):
            self.advance()
            self.match_type(TT.COMMA)
            return ExitNode(line=line)

        # ── Условие: Суд вершу:
        if self.at_kw('Суд вершу:'):
            return self.parse_if(line)

        # ── Цикл while с условием
        if self.at_kw('Коловрат покуда'):
            self.advance()
            cond = self.parse_condition()
            self.match_type(TT.COLON)
            body = self.parse_indented_block()
            return WhileNode(line=line, condition=cond, body=body)

        # ── Цикл while True (Коловрат: или Коловрат)
        if self.at_kw('Коловрат:', 'Коловрат'):
            self.advance()
            self.match_type(TT.COLON)
            body = self.parse_indented_block()
            return WhileNode(line=line, condition=None, body=body)

        # ── For по диапазону: Странствие <Имя> по землям от <A> до <B>:
        if self.at_kw('Странствие'):
            return self.parse_for(line)

        # ── Определение функции
        if self.at_kw('Умение нарекаю'):
            return self.parse_funcdef(line)

        # ── Вызов функции: Призвать умение <Имя>(...)
        if self.at_kw('Призвать умение'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            args = self.parse_call_args()
            self.match_type(TT.COMMA)
            return FuncCallNode(line=line, name=name, args=args)

        # ── Список: Дружина именем <Имя> с ратниками [...]
        if self.at_kw('Дружина именем'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            self.expect_kw('с ратниками')
            elems = self.parse_list_literal()
            self.match_type(TT.COMMA)
            return AssignNode(line=line, name=name, value=elems)

        # ── Append: Принять в дружину <Имя> ратника <expr>
        if self.at_kw('Принять в дружину'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            self.expect_kw('ратника')
            value = self.parse_expression()
            self.match_type(TT.COMMA)
            return ListAppendNode(line=line, name=name, value=value)

        # ── Pop: Изгнать из дружины <Имя> ратника с позиции <expr>
        if self.at_kw('Изгнать из дружины'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            self.expect_kw('ратника с позиции')
            idx = self.parse_expression()
            self.match_type(TT.COMMA)
            return ListPopNode(line=line, name=name, index=idx)

        # ── Добавить в сундук <Имя> единицу малую  (+=1)
        if self.at_kw('Добавить в сундук'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            if self.match_kw('единицу малую'):
                self.match_type(TT.COMMA)
                return AugAssignNode(line=line, name=name, op='+=', value=NumberNode(line=line, value=1))
            elif self.match_kw('единицу'):
                self.match_type(TT.COMMA)
                return AugAssignNode(line=line, name=name, op='+=', value=NumberNode(line=line, value=1))
            else:
                value = self.parse_expression()
                self.match_type(TT.COMMA)
                return AugAssignNode(line=line, name=name, op='+=', value=value)

        # ── Убавить из сундука <Имя> единицу
        if self.at_kw('Убавить из сундука'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            self.match_kw('единицу малую', 'единицу')
            self.match_type(TT.COMMA)
            return AugAssignNode(line=line, name=name, op='-=', value=NumberNode(line=line, value=1))

        raise ParseError(line, f"Неведомое начало инструкции: '{tok.value}'")

    # ── If ──────────────────────────────────────────────────────────
    def parse_if(self, line: int) -> IfNode:
        self.expect_kw('Суд вершу:')
        self.skip_newlines()
        branches = []

        # Ожидаем INDENT
        if self.at_type(TT.INDENT):
            self.advance()

        while True:
            self.skip_newlines()
            if self.at_kw('Иначе коль'):
                self.advance()
                cond = self.parse_condition()
                self.match_type(TT.COLON)
                body = self.parse_indented_block()
                branches.append((cond, body))
            elif self.at_kw('Иначе:'):
                self.advance()
                body = self.parse_indented_block()
                branches.append((None, body))
                break
            elif self.at_kw('Коль'):
                self.advance()
                cond = self.parse_condition()
                self.match_type(TT.COLON)
                body = self.parse_indented_block()
                branches.append((cond, body))
            else:
                break

        if self.at_type(TT.DEDENT):
            self.advance()

        return IfNode(line=line, branches=branches)

    # ── For ─────────────────────────────────────────────────────────
    def parse_for(self, line: int) -> ForNode:
        self.expect_kw('Странствие')
        var = self.expect_type(TT.IDENT).value

        if self.match_kw('по землям от'):
            start = self.parse_atom()
            self.expect_kw('до')
            end = self.parse_atom()
            self.match_type(TT.COLON)
            body = self.parse_indented_block()
            iterable = RangeNode(line=line, start=start, end=end)
        elif self.match_kw('по дружине'):
            iterable = self.parse_atom()
            self.match_type(TT.COLON)
            body = self.parse_indented_block()
        else:
            raise ParseError(line, "Ожидалось 'по землям от' или 'по дружине'")

        return ForNode(line=line, var=var, iterable=iterable, body=body)

    # ── FuncDef ─────────────────────────────────────────────────────
    def parse_funcdef(self, line: int) -> FuncDefNode:
        self.expect_kw('Умение нарекаю')
        name = self.expect_type(TT.IDENT).value
        params = self.parse_params()
        self.match_type(TT.COLON)
        body = self.parse_indented_block()
        return FuncDefNode(line=line, name=name, params=params, body=body)

    def parse_params(self) -> List[str]:
        params = []
        self.match_type(TT.LPAREN)
        while self.at_type(TT.IDENT):
            params.append(self.advance().value)
            if not self.match_type(TT.COMMA):
                break
        self.match_type(TT.RPAREN)
        return params

    def parse_call_args(self) -> List[Node]:
        args = []
        self.match_type(TT.LPAREN)
        while not self.at_type(TT.RPAREN, TT.COMMA, TT.NEWLINE, TT.EOF):
            args.append(self.parse_expression())
            if not self.match_type(TT.COMMA):
                break
        self.match_type(TT.RPAREN)
        return args

    def parse_list_literal(self) -> ListNode:
        line = self.current().line
        elems = []
        self.expect_type(TT.LBRACKET)
        while not self.at_type(TT.RBRACKET, TT.EOF):
            elems.append(self.parse_expression())
            self.match_type(TT.COMMA)
        self.expect_type(TT.RBRACKET)
        return ListNode(line=line, elements=elems)

    # ── Выражения ───────────────────────────────────────────────────
    def parse_expression(self) -> Node:
        """Разбирает арифметическое выражение или строку"""
        return self.parse_additive()

    def parse_additive(self) -> Node:
        left = self.parse_multiplicative()
        while True:
            if self.at_kw('сложить с'):
                op = self.advance().value
                right = self.parse_multiplicative()
                left = BinOpNode(line=left.line, left=left, op='+', right=right)
            elif self.at_kw('отнять'):
                op = self.advance().value
                right = self.parse_multiplicative()
                left = BinOpNode(line=left.line, left=left, op='-', right=right)
            else:
                break
        return left

    def parse_multiplicative(self) -> Node:
        left = self.parse_unary()
        while True:
            if self.at_kw('умножить на'):
                self.advance()
                right = self.parse_unary()
                left = BinOpNode(line=left.line, left=left, op='*', right=right)
            elif self.at_kw('разделить на'):
                self.advance()
                right = self.parse_unary()
                left = BinOpNode(line=left.line, left=left, op='/', right=right)
            elif self.at_kw('остаток от деления на'):
                self.advance()
                right = self.parse_unary()
                left = BinOpNode(line=left.line, left=left, op='%', right=right)
            else:
                break
        return left

    def parse_unary(self) -> Node:
        return self.parse_cast()

    def parse_cast(self) -> Node:
        line = self.current().line
        # оборотить <expr> в Число Цельное / Дробное / Слово
        if self.at_kw('оборотить'):
            self.advance()
            value = self.parse_atom()
            if self.match_kw('в Число Цельное'):
                return CastNode(line=line, cast_type='int', value=value)
            elif self.match_kw('в Число Дробное'):
                return CastNode(line=line, cast_type='float', value=value)
            elif self.match_kw('в Слово'):
                return CastNode(line=line, cast_type='str', value=value)
            return value
        return self.parse_atom()

    def parse_atom(self) -> Node:
        tok = self.current()
        line = tok.line

        # Числа
        if tok.type == TT.NUMBER:
            self.advance()
            val = float(tok.value) if '.' in tok.value else int(tok.value)
            return NumberNode(line=line, value=val)

        # Строки
        if tok.type == TT.STRING:
            self.advance()
            return StringNode(line=line, raw=tok.value)

        # Булевы
        if self.at_kw('Зрю истину'):
            self.advance()
            return BoolNode(line=line, value=True)
        if self.at_kw('Зрю ложь'):
            self.advance()
            return BoolNode(line=line, value=False)
        if self.at_kw('ничто'):
            self.advance()
            return NoneNode(line=line)

        # Случайное число: из палат случайных призвать число от <A> до <B>
        if self.at_kw('из палат случайных призвать число от'):
            self.advance()
            low = self.parse_atom()
            self.expect_kw('до')
            high = self.parse_atom()
            return RandomNode(line=line, low=low, high=high)

        # длина дружины <expr>
        if self.at_kw('длина дружины'):
            self.advance()
            value = self.parse_atom()
            return LenNode(line=line, value=value)

        # Ратник под номером <индекс> в дружине <Имя>
        if self.at_kw('Ратник под номером'):
            self.advance()
            idx = self.parse_atom()
            self.expect_kw('в дружине')
            name = self.expect_type(TT.IDENT).value
            return IndexNode(line=line, collection=VarNode(line=line, name=name), index=idx)

        # Вызов функции: Призвать умение <Имя>(...)
        if self.at_kw('Призвать умение'):
            self.advance()
            name = self.expect_type(TT.IDENT).value
            args = self.parse_call_args()
            return FuncCallNode(line=line, name=name, args=args)

        # Список-литерал [...]
        if tok.type == TT.LBRACKET:
            return self.parse_list_literal()

        # Скобки
        if tok.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect_type(TT.RPAREN)
            return expr

        # Идентификатор (переменная)
        if tok.type == TT.IDENT:
            self.advance()
            return VarNode(line=line, name=tok.value)

        raise ParseError(line, f"Ожидалось выражение, а явилось '{tok.value}'")

    # ── Условия (для if / while) ─────────────────────────────────────
    def parse_condition(self) -> Node:
        return self.parse_or()

    def parse_or(self) -> Node:
        left = self.parse_and()
        while self.at_kw('либо же'):
            self.advance()
            right = self.parse_and()
            left = BinOpNode(line=left.line, left=left, op='or', right=right)
        return left

    def parse_and(self) -> Node:
        left = self.parse_not()
        while self.at_kw('и к тому же'):
            self.advance()
            right = self.parse_not()
            left = BinOpNode(line=left.line, left=left, op='and', right=right)
        return left

    def parse_not(self) -> Node:
        line = self.current().line
        if self.at_kw('не есть'):
            self.advance()
            operand = self.parse_comparison()
            return UnaryOpNode(line=line, op='not', operand=operand)
        return self.parse_comparison()

    def parse_comparison(self) -> Node:
        left = self.parse_expression()
        CMP_OPS = {
            'в точности как': '==',
            'не ровня': '!=',
            'меньше': '<',
            'больше': '>',
            'не меньше': '>=',
            'не больше': '<=',
        }
        for kw, op in CMP_OPS.items():
            if self.at_kw(kw):
                self.advance()
                right = self.parse_expression()
                return BinOpNode(line=left.line, left=left, op=op, right=right)
        return left
