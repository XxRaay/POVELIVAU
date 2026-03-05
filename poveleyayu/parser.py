import re

from .errors import ParseError
from .lexer import Token
from . import nodes as n


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> n.Program:
        if not self.tokens:
            raise ParseError(1, "Свиток ...", "пусто")
        first = self.tokens[0]
        if not first.value.startswith("Свиток "):
            raise ParseError(first.line, "Свиток ...", first.value)
        self.pos = 1
        body = self._parse_block(0)
        if self.pos >= len(self.tokens) or self.tokens[self.pos].value != "Повелеваю: Начать выполнение!":
            line = self.tokens[self.pos - 1].line if self.pos else 1
            raise ParseError(line, "Повелеваю: Начать выполнение!", "конец свитка")
        return n.Program(line=first.line, header=first.value, body=body)

    def _parse_block(self, indent: int) -> list[n.Node]:
        out: list[n.Node] = []
        while self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            if t.indent < indent:
                break
            if t.indent > indent:
                raise ParseError(t.line, f"отступ уровня {indent}", f"отступ уровня {t.indent}")
            if t.value == "Повелеваю: Начать выполнение!":
                break
            out.append(self._parse_stmt(indent))
        return out

    def _parse_stmt(self, indent: int) -> n.Node:
        t = self.tokens[self.pos]
        text = t.value
        line = t.line

        if text.startswith(("Глаголю народу:", "Вещаю:", "Кричу на всю Русь:")):
            expr = text.split(":", 1)[1].strip().rstrip(",")
            self.pos += 1
            return n.PrintNode(line=line, expr=n.RawExprNode(line=line, text=expr))

        if text.startswith("Повелеваю: Отныне ") and " именоваться " in text:
            tail = text[len("Повелеваю: Отныне "):].rstrip(",")
            expr, name = tail.rsplit(" именоваться ", 1)
            self.pos += 1
            return n.AssignNode(line=line, name=name.strip(), expr=n.RawExprNode(line=line, text=expr.strip()))

        if text.startswith("Указываю: Сотворить сундук пустой, именем "):
            m = re.match(r"Указываю: Сотворить сундук пустой, именем (\w+), и положить в него (.+),$", text)
            if not m:
                raise ParseError(line, "создание сундука", text)
            self.pos += 1
            return n.AssignNode(line=line, name=m.group(1), expr=n.RawExprNode(line=line, text=m.group(2)))

        if text.startswith("Повелеваю: Взять слово от гостя заезжего"):
            self.pos += 1
            cast = None
            m = re.match(r"Повелеваю: Взять слово от гостя заезжего и наречь (\w+),$", text)
            if m:
                return n.InputNode(line=line, name=m.group(1))
            m = re.match(r"Повелеваю: Взять слово от гостя заезжего, оборотить его в (Число Цельное|Число Дробное) и наречь (\w+),$", text)
            if m:
                cast = "int" if m.group(1) == "Число Цельное" else "float"
                return n.InputNode(line=line, name=m.group(2), cast=cast)
            raise ParseError(line, "команда ввода", text)

        if text.startswith("Вопрошаю гостя:"):
            m = re.match(r'Вопрошаю гостя: (".*") и наречь (\w+),$', text)
            if not m:
                raise ParseError(line, "Вопрошаю ...", text)
            self.pos += 1
            return n.InputNode(line=line, name=m.group(2), prompt=n.RawExprNode(line=line, text=m.group(1)))

        if text == "Суд вершу:":
            return self._parse_if(indent)

        if text == "Коловрат:" or text.startswith("Коловрат покуда "):
            return self._parse_while(indent)

        if text.startswith("Странствие "):
            return self._parse_for(indent)

        if text == "Повелеваю: Пресечь бег сего коловрата,":
            self.pos += 1
            return n.BreakNode(line=line)

        if text == "Повелеваю: Перейти к следующему витку,":
            self.pos += 1
            return n.ContinueNode(line=line)

        if text.startswith("Умение нарекаю "):
            return self._parse_funcdef(indent)

        if text.startswith("Повелеваю: Вернуть "):
            self.pos += 1
            expr = text[len("Повелеваю: Вернуть "):].rstrip(",")
            return n.ReturnNode(line=line, expr=n.RawExprNode(line=line, text=expr))

        if text.startswith("Призвать умение "):
            self.pos += 1
            call = text[len("Призвать умение "):].rstrip(",")
            return n.ExprStmtNode(line=line, expr=n.RawExprNode(line=line, text=call))

        if text.startswith("Дружина именем "):
            m = re.match(r"Дружина именем (\w+) с ратниками (\[.*\]),$", text)
            if not m:
                raise ParseError(line, "Дружина именем...", text)
            self.pos += 1
            return n.AssignNode(line=line, name=m.group(1), expr=n.RawExprNode(line=line, text=m.group(2)))

        if text.startswith("Принять в дружину "):
            m = re.match(r"Принять в дружину (\w+) ратника (.+),$", text)
            if not m:
                raise ParseError(line, "append", text)
            self.pos += 1
            return n.ListAppendNode(line=line, name=m.group(1), value=n.RawExprNode(line=line, text=m.group(2)))

        if text.startswith("Изгнать из дружины "):
            m = re.match(r"Изгнать из дружины (\w+) ратника с позиции (.+),$", text)
            if not m:
                raise ParseError(line, "pop", text)
            self.pos += 1
            return n.ListPopNode(line=line, name=m.group(1), index=n.RawExprNode(line=line, text=m.group(2)))

        if text.startswith("Добавить в сундук "):
            self.pos += 1
            m = re.match(r"Добавить в сундук (\w+) единицу малую,$", text)
            if m:
                return n.IncrementNode(line=line, name=m.group(1), delta=n.RawExprNode(line=line, text="1"))
            m = re.match(r"Добавить в сундук (\w+) (.+),$", text)
            if m:
                return n.IncrementNode(line=line, name=m.group(1), delta=n.RawExprNode(line=line, text=m.group(2)))
            raise ParseError(line, "Добавить ...", text)

        if text.startswith("Убавить из сундука "):
            m = re.match(r"Убавить из сундука (\w+) единицу,$", text)
            if not m:
                raise ParseError(line, "Убавить ...", text)
            self.pos += 1
            return n.DecrementNode(line=line, name=m.group(1))

        if text == "Повелеваю: Остановить всё и почить,":
            self.pos += 1
            return n.ExitNode(line=line)

        raise ParseError(line, "известная команда", text)

    def _parse_if(self, indent: int) -> n.IfNode:
        line = self.tokens[self.pos].line
        self.pos += 1
        branches: list[n.IfBranch] = []
        else_body: list[n.Node] = []
        while self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            if t.indent != indent + 1:
                break
            if t.value.startswith("Коль ") and t.value.endswith(":"):
                cond = t.value[len("Коль "):-1].strip()
                self.pos += 1
                body = self._parse_block(indent + 2)
                branches.append(n.IfBranch(line=t.line, condition=n.RawExprNode(line=t.line, text=cond), body=body))
            elif t.value.startswith("Иначе коль ") and t.value.endswith(":"):
                cond = t.value[len("Иначе коль "):-1].strip()
                self.pos += 1
                body = self._parse_block(indent + 2)
                branches.append(n.IfBranch(line=t.line, condition=n.RawExprNode(line=t.line, text=cond), body=body))
            elif t.value == "Иначе:":
                self.pos += 1
                else_body = self._parse_block(indent + 2)
                break
            else:
                raise ParseError(t.line, "Коль/Иначе коль/Иначе", t.value)
        return n.IfNode(line=line, branches=branches, else_body=else_body)

    def _parse_while(self, indent: int) -> n.WhileNode:
        t = self.tokens[self.pos]
        self.pos += 1
        cond = None
        if t.value.startswith("Коловрат покуда ") and t.value.endswith(":"):
            cond = n.RawExprNode(line=t.line, text=t.value[len("Коловрат покуда "):-1].strip())
        body = self._parse_block(indent + 1)
        return n.WhileNode(line=t.line, condition=cond, body=body)

    def _parse_for(self, indent: int):
        t = self.tokens[self.pos]
        text = t.value
        self.pos += 1
        m = re.match(r"Странствие (\w+) по землям от (.+) до (.+):$", text)
        if m:
            body = self._parse_block(indent + 1)
            return n.ForRangeNode(line=t.line, var_name=m.group(1), start=n.RawExprNode(text=m.group(2), line=t.line), end=n.RawExprNode(text=m.group(3), line=t.line), body=body)
        m = re.match(r"Странствие (\w+) по дружине (\w+):$", text)
        if m:
            body = self._parse_block(indent + 1)
            return n.ForEachNode(line=t.line, var_name=m.group(1), iterable=n.RawExprNode(line=t.line, text=m.group(2)), body=body)
        raise ParseError(t.line, "Странствие", text)

    def _parse_funcdef(self, indent: int):
        t = self.tokens[self.pos]
        m = re.match(r"Умение нарекаю (\w+)\((.*)\):$", t.value)
        if not m:
            raise ParseError(t.line, "Умение нарекаю ...", t.value)
        self.pos += 1
        params = [p.strip() for p in m.group(2).split(",") if p.strip()] if m.group(2).strip() else []
        body = self._parse_block(indent + 1)
        return n.FuncDefNode(line=t.line, name=m.group(1), params=params, body=body)
