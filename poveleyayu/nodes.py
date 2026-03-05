from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Node:
    line: int = 0


@dataclass
class Program(Node):
    header: str = ""
    body: list[Node] = field(default_factory=list)


@dataclass
class Expr(Node):
    pass


@dataclass
class NumberNode(Expr):
    value: float | int = 0


@dataclass
class StringNode(Expr):
    value: str = ""


@dataclass
class BoolNode(Expr):
    value: bool = False


@dataclass
class NoneNode(Expr):
    pass


@dataclass
class VarNode(Expr):
    name: str = ""


@dataclass
class ListNode(Expr):
    elements: list[Expr] = field(default_factory=list)


@dataclass
class IndexNode(Expr):
    collection: Expr | None = None
    index: Expr | None = None


@dataclass
class UnaryOpNode(Expr):
    op: str = ""
    operand: Expr | None = None


@dataclass
class BinOpNode(Expr):
    left: Expr | None = None
    op: str = ""
    right: Expr | None = None


@dataclass
class FuncCallNode(Expr):
    name: str = ""
    args: list[Expr] = field(default_factory=list)


@dataclass
class RawExprNode(Expr):
    text: str = ""


@dataclass
class AssignNode(Node):
    name: str = ""
    expr: Expr | None = None


@dataclass
class PrintNode(Node):
    expr: Expr | None = None


@dataclass
class InputNode(Node):
    name: str = ""
    prompt: Optional[Expr] = None
    cast: Optional[str] = None


@dataclass
class IfBranch(Node):
    condition: Optional[Expr] = None
    body: list[Node] = field(default_factory=list)


@dataclass
class IfNode(Node):
    branches: list[IfBranch] = field(default_factory=list)
    else_body: list[Node] = field(default_factory=list)


@dataclass
class WhileNode(Node):
    condition: Optional[Expr] = None
    body: list[Node] = field(default_factory=list)


@dataclass
class ForRangeNode(Node):
    var_name: str = ""
    start: Expr | None = None
    end: Expr | None = None
    body: list[Node] = field(default_factory=list)


@dataclass
class ForEachNode(Node):
    var_name: str = ""
    iterable: Expr | None = None
    body: list[Node] = field(default_factory=list)


@dataclass
class BreakNode(Node):
    pass


@dataclass
class ContinueNode(Node):
    pass


@dataclass
class ReturnNode(Node):
    expr: Optional[Expr] = None


@dataclass
class FuncDefNode(Node):
    name: str = ""
    params: list[str] = field(default_factory=list)
    body: list[Node] = field(default_factory=list)


@dataclass
class ExprStmtNode(Node):
    expr: Expr | None = None


@dataclass
class ListAppendNode(Node):
    name: str = ""
    value: Expr | None = None


@dataclass
class ListPopNode(Node):
    name: str = ""
    index: Expr | None = None


@dataclass
class IncrementNode(Node):
    name: str = ""
    delta: Expr | None = None


@dataclass
class DecrementNode(Node):
    name: str = ""


@dataclass
class ExitNode(Node):
    pass
