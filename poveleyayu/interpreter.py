import re

from . import nodes as n
from .errors import RuntimeError
from .stdlib import random_between


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class UserFunction:
    def __init__(self, node, interpreter):
        self.node = node
        self.interpreter = interpreter

    def __call__(self, *args):
        scope = {name: value for name, value in zip(self.node.params, args)}
        self.interpreter.scopes.append(scope)
        try:
            for stmt in self.node.body:
                self.interpreter.execute(stmt)
        except ReturnSignal as r:
            return r.value
        finally:
            self.interpreter.scopes.pop()
        return None


class Interpreter:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.scopes = [{}]
        self.globals = {
            "длина": len,
            "оборотить_в_целое": int,
            "оборотить_в_дробное": float,
            "оборотить_в_слово": str,
            "случайное_число": random_between,
        }

    def run(self, program: n.Program):
        for stmt in program.body:
            self.execute(stmt)

    def execute(self, node):
        method = getattr(self, f"visit_{type(node).__name__}")
        return method(node)

    def visit_AssignNode(self, node):
        self._set(node.name, self.eval_expr(node.expr))

    def visit_PrintNode(self, node):
        val = self.eval_expr(node.expr)
        print(self._interpolate(val) if isinstance(val, str) else val)

    def visit_InputNode(self, node):
        prompt = self.eval_expr(node.prompt) if node.prompt else ""
        value = input(prompt)
        if node.cast == "int":
            value = int(value)
        elif node.cast == "float":
            value = float(value)
        self._set(node.name, value)

    def visit_IfNode(self, node):
        for br in node.branches:
            if self.eval_expr(br.condition):
                for stmt in br.body:
                    self.execute(stmt)
                return
        for stmt in node.else_body:
            self.execute(stmt)

    def visit_WhileNode(self, node):
        while True:
            if node.condition is not None and not self.eval_expr(node.condition):
                break
            try:
                for stmt in node.body:
                    self.execute(stmt)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def visit_ForRangeNode(self, node):
        start = int(self.eval_expr(node.start))
        end = int(self.eval_expr(node.end))
        for i in range(start, end + 1):
            self._set(node.var_name, i)
            try:
                for stmt in node.body:
                    self.execute(stmt)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def visit_ForEachNode(self, node):
        for item in self.eval_expr(node.iterable):
            self._set(node.var_name, item)
            try:
                for stmt in node.body:
                    self.execute(stmt)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def visit_BreakNode(self, node):
        raise BreakSignal()

    def visit_ContinueNode(self, node):
        raise ContinueSignal()

    def visit_ReturnNode(self, node):
        raise ReturnSignal(self.eval_expr(node.expr) if node.expr else None)

    def visit_FuncDefNode(self, node):
        self._set(node.name, UserFunction(node, self))

    def visit_ExprStmtNode(self, node):
        self.eval_expr(node.expr)

    def visit_ListAppendNode(self, node):
        self._get(node.name).append(self.eval_expr(node.value))

    def visit_ListPopNode(self, node):
        self._get(node.name).pop(int(self.eval_expr(node.index)))

    def visit_IncrementNode(self, node):
        self._set(node.name, self._get(node.name) + self.eval_expr(node.delta))

    def visit_DecrementNode(self, node):
        self._set(node.name, self._get(node.name) - 1)

    def visit_ExitNode(self, node):
        raise SystemExit(0)

    def eval_expr(self, expr):
        if isinstance(expr, n.RawExprNode):
            return self._eval_raw(expr.text)
        return expr

    def _eval_raw(self, text: str):
        py = self._translate_expr(text)
        env = dict(self.globals)
        for scope in self.scopes:
            env.update(scope)
        try:
            return eval(py, {"__builtins__": {}}, env)
        except NameError as e:
            name = str(e).split("'")[1]
            raise RuntimeError.undefined_name(name) from e
        except ZeroDivisionError as e:
            raise RuntimeError.division_by_zero() from e

    def _translate_expr(self, text: str) -> str:
        t = text.strip()
        if t.startswith('"') and t.endswith('"'):
            return repr(self._interpolate(t[1:-1]))

        replacements = [
            (" в точности как ", " == "),
            (" не ровня ", " != "),
            (" не меньше ", " >= "),
            (" не больше ", " <= "),
            (" меньше ", " < "),
            (" больше ", " > "),
            (" и к тому же ", " and "),
            (" либо же ", " or "),
            ("не есть ", "not "),
            (" сложить с ", " + "),
            (" отнять ", " - "),
            (" умножить на ", " * "),
            (" разделить на ", " / "),
            (" остаток от деления на ", " % "),
            ("Зрю истину", "True"),
            ("Зрю ложь", "False"),
            ("ничто", "None"),
        ]
        for a, b in replacements:
            t = t.replace(a, b)

        t = re.sub(r"из палат случайных призвать число от\s+(.+?)\s+до\s+(.+)$", r"случайное_число(\1, \2)", t)
        t = re.sub(r"длина дружины\s+(\w+)", r"длина(\1)", t)
        t = re.sub(r"оборотить\s+(.+?)\s+в Число Цельное", r"оборотить_в_целое(\1)", t)
        t = re.sub(r"оборотить\s+(.+?)\s+в Число Дробное", r"оборотить_в_дробное(\1)", t)
        t = re.sub(r"оборотить\s+(.+?)\s+в Слово", r"оборотить_в_слово(\1)", t)
        t = re.sub(r"Ратник под номером\s+(.+?)\s+в дружине\s+(\w+)", r"\2[\1]", t)
        return t

    def _interpolate(self, text: str):
        def repl(m):
            return str(self._get(m.group(1)))

        return re.sub(r"\[(\w+)\]", repl, text)

    def _set(self, name, value):
        self.scopes[-1][name] = value

    def _get(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise RuntimeError.undefined_name(name)
