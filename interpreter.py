# interpreter.py — Интерпретатор языка ПОВЕЛЕВАЮ (паттерн Visitor)
import re
import sys
from typing import Any, Dict, List, Optional
from nodes import *
from errors import (
    PovelRuntimeError, UndefinedVariableError, DivisionByZeroError,
    TypePovelError, ReturnSignal, BreakSignal, ContinueSignal
)
import stdlib
import requests


class Environment:
    """Стек областей видимости"""
    def __init__(self):
        self.scopes: List[Dict[str, Any]] = [{}]  # глобальная область

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def get(self, name: str) -> Any:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise UndefinedVariableError(name)

    def set(self, name: str, value: Any):
        # Если переменная уже существует в любой области — обновляем её
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return
        # Иначе создаём в текущей (верхней) области
        self.scopes[-1][name] = value

    def set_local(self, name: str, value: Any):
        self.scopes[-1][name] = value

    def set_global(self, name: str, value: Any):
        self.scopes[0][name] = value


class Function:
    def __init__(self, name: str, params: List[str], body: List[Node], env: Environment):
        self.name = name
        self.params = params
        self.body = body
        self.closure = env  # для замыканий (упрощённо — передаём среду)


class Interpreter:
    def __init__(self, debug: bool = False):
        self.env = Environment()
        self.debug = debug

    # ── Главный метод ───────────────────────────────────────────────
    def execute(self, node: Node) -> Any:
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node):
        raise PovelRuntimeError(f"Неведомый узел дерева: {type(node).__name__}")

    def exec_block(self, stmts: List[Node]):
        for stmt in stmts:
            self.execute(stmt)

    # ── Программа ───────────────────────────────────────────────────
    def visit_ProgramNode(self, node: ProgramNode):
        if self.debug:
            print(f"[ОТЛАДКА] Свиток: {node.scroll_type!r}, Название: {node.title!r}")
        self.exec_block(node.body)

    # ── Присвоение ──────────────────────────────────────────────────
    def visit_AssignNode(self, node: AssignNode):
        value = self.execute(node.value)
        self.env.set(node.name, value)

    def visit_AugAssignNode(self, node: AugAssignNode):
        current = self.env.get(node.name)
        delta = self.execute(node.value)
        if node.op == '+=':
            self.env.set(node.name, current + delta)
        elif node.op == '-=':
            self.env.set(node.name, current - delta)

    # ── Вывод ───────────────────────────────────────────────────────
    def visit_PrintNode(self, node: PrintNode):
        value = self.execute(node.value)
        print(value)

    # ── Ввод ────────────────────────────────────────────────────────
    def visit_InputNode(self, node: InputNode):
        if node.prompt:
            prompt_text = self.execute(node.prompt)
            raw = input(str(prompt_text))
        else:
            raw = input()
        if node.cast == 'int':
            value = int(raw)
        elif node.cast == 'float':
            value = float(raw)
        else:
            value = raw
        self.env.set(node.name, value)

    # ── Условие ─────────────────────────────────────────────────────
    def visit_IfNode(self, node: IfNode):
        for condition, body in node.branches:
            if condition is None:
                # else-ветка
                self.exec_block(body)
                return
            if self.execute(condition):
                self.exec_block(body)
                return

    # ── While ───────────────────────────────────────────────────────
    def visit_WhileNode(self, node: WhileNode):
        while True:
            if node.condition is not None:
                if not self.execute(node.condition):
                    break
            try:
                self.exec_block(node.body)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    # ── Break / Continue ────────────────────────────────────────────
    def visit_BreakNode(self, node: BreakNode):
        raise BreakSignal()

    def visit_ContinueNode(self, node: ContinueNode):
        raise ContinueSignal()

    # ── For ─────────────────────────────────────────────────────────
    def visit_ForNode(self, node: ForNode):
        if isinstance(node.iterable, RangeNode):
            start = int(self.execute(node.iterable.start))
            end = int(self.execute(node.iterable.end))
            iterable = range(start, end + 1)
        else:
            iterable = self.execute(node.iterable)

        for item in iterable:
            self.env.set(node.var, item)
            try:
                self.exec_block(node.body)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    # ── Функции ─────────────────────────────────────────────────────
    def visit_FuncDefNode(self, node: FuncDefNode):
        func = Function(node.name, node.params, node.body, self.env)
        self.env.set(node.name, func)

    def visit_FuncCallNode(self, node: FuncCallNode) -> Any:
        func = self.env.get(node.name)
        if not isinstance(func, Function):
            raise PovelRuntimeError(f"'{node.name}' — не умение, а иное")
        args = [self.execute(a) for a in node.args]
        if len(args) != len(func.params):
            raise PovelRuntimeError(
                f"Умение '{node.name}' ожидает {len(func.params)} аргументов, "
                f"но получило {len(args)}"
            )
        self.env.push()
        for param, val in zip(func.params, args):
            self.env.set_local(param, val)
        result = None
        try:
            self.exec_block(func.body)
        except ReturnSignal as r:
            result = r.value
        finally:
            self.env.pop()
        return result

    def visit_ReturnNode(self, node: ReturnNode):
        value = self.execute(node.value) if node.value else None
        raise ReturnSignal(value)

    # ── Списки ──────────────────────────────────────────────────────
    def visit_ListNode(self, node: ListNode) -> list:
        return [self.execute(e) for e in node.elements]

    def visit_ListAppendNode(self, node: ListAppendNode):
        lst = self.env.get(node.name)
        value = self.execute(node.value)
        lst.append(value)

    def visit_ListPopNode(self, node: ListPopNode):
        lst = self.env.get(node.name)
        idx = self.execute(node.index)
        lst.pop(int(idx))

    def visit_IndexNode(self, node: IndexNode) -> Any:
        collection = self.execute(node.collection)
        idx = int(self.execute(node.index))
        try:
            return collection[idx]
        except IndexError:
            raise PovelRuntimeError(f"Ратник под номером {idx} не найден в дружине!")

    # ── Математика ──────────────────────────────────────────────────
    def visit_BinOpNode(self, node: BinOpNode) -> Any:
        left = self.execute(node.left)
        right = self.execute(node.right)
        op = node.op
        try:
            if op == '+':   return left + right
            if op == '-':   return left - right
            if op == '*':   return left * right
            if op == '/':
                if right == 0:
                    raise DivisionByZeroError()
                return left / right
            if op == '%':   return left % right
            if op == '==':  return left == right
            if op == '!=':  return left != right
            if op == '<':   return left < right
            if op == '>':   return left > right
            if op == '>=':  return left >= right
            if op == '<=':  return left <= right
            if op == 'and': return left and right
            if op == 'or':  return left or right
        except TypeError as e:
            raise TypePovelError(str(e))
        raise PovelRuntimeError(f"Неведомый оператор: {op}")

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        val = self.execute(node.operand)
        if node.op == 'not':
            return not val
        raise PovelRuntimeError(f"Неведомый унарный оператор: {node.op}")

    # ── Литералы ────────────────────────────────────────────────────
    def visit_NumberNode(self, node: NumberNode) -> Any:
        return node.value

    def visit_StringNode(self, node: StringNode) -> str:
        """Интерполяция строк: [ИмяПеременной] → значение"""
        raw = node.raw
        def replace_var(m):
            name = m.group(1)
            return str(self.env.get(name))
        return re.sub(r'\[([А-ЯЁа-яёA-Za-z_][А-ЯЁа-яёA-Za-z0-9_]*)\]', replace_var, raw)

    def visit_BoolNode(self, node: BoolNode) -> bool:
        return node.value

    def visit_NoneNode(self, node: NoneNode):
        return None

    def visit_VarNode(self, node: VarNode) -> Any:
        return self.env.get(node.name)

    # ── Стандартная библиотека ───────────────────────────────────────
    def visit_RandomNode(self, node: RandomNode) -> int:
        low = self.execute(node.low)
        high = self.execute(node.high)
        return stdlib.randint(low, high)

    def visit_LenNode(self, node: LenNode) -> int:
        value = self.execute(node.value)
        return stdlib.length(value)

    def visit_CastNode(self, node: CastNode) -> Any:
        value = self.execute(node.value)
        try:
            if node.cast_type == 'int':   return int(value)
            if node.cast_type == 'float': return float(value)
            if node.cast_type == 'str':   return str(value)
        except (ValueError, TypeError) as e:
            raise TypePovelError(str(e))

    def visit_ExitNode(self, node: ExitNode):
        print("— Всё. Почиваю. —")
        sys.exit(0)

    def visit_HttpGetNode(self, node: HttpGetNode) -> str:
        url = self.execute(node.url)
        try:
            response = requests.get(url, timeout=5)
        except requests.RequestException as exc:
            raise PovelRuntimeError(
                f"Вестник не смог достигнуть земель по адресу '{url}': {exc}"
            )
        return response.text

    def visit_HttpPostNode(self, node: HttpPostNode) -> str:
        url = self.execute(node.url)
        body = self.execute(node.body)
        try:
            response = requests.post(url, data=str(body), timeout=5)
        except requests.RequestException as exc:
            raise PovelRuntimeError(
                f"Вестник с вестью не дошёл до земель по адресу '{url}': {exc}"
            )
        return response.text

    # ── RangeNode (используется только в ForNode) ────────────────────
    def visit_RangeNode(self, node: RangeNode):
        start = int(self.execute(node.start))
        end = int(self.execute(node.end))
        return range(start, end + 1)
