# nodes.py — AST-узлы языка ПОВЕЛЕВАЮ
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class Node:
    line: int = field(default=0, kw_only=True)


@dataclass
class ProgramNode(Node):
    title: str
    scroll_type: str
    body: List[Node]


@dataclass
class AssignNode(Node):
    name: str
    value: 'Node'


@dataclass
class PrintNode(Node):
    value: 'Node'


@dataclass
class InputNode(Node):
    name: str
    prompt: Optional['Node'] = None
    cast: Optional[str] = None   # 'int', 'float', or None


@dataclass
class IfNode(Node):
    branches: List[tuple]   # list of (condition_node | None, body_nodes)


@dataclass
class WhileNode(Node):
    condition: Optional['Node']   # None = while True
    body: List[Node]


@dataclass
class BreakNode(Node):
    pass


@dataclass
class ContinueNode(Node):
    pass


@dataclass
class ForNode(Node):
    var: str
    iterable: 'Node'         # RangeNode or identifier
    body: List[Node]


@dataclass
class RangeNode(Node):
    start: 'Node'
    end: 'Node'


@dataclass
class FuncDefNode(Node):
    name: str
    params: List[str]
    body: List[Node]


@dataclass
class ReturnNode(Node):
    value: Optional['Node']


@dataclass
class FuncCallNode(Node):
    name: str
    args: List['Node']


@dataclass
class BinOpNode(Node):
    left: 'Node'
    op: str
    right: 'Node'


@dataclass
class UnaryOpNode(Node):
    op: str
    operand: 'Node'


@dataclass
class NumberNode(Node):
    value: Any


@dataclass
class StringNode(Node):
    raw: str          # raw template string with [Var] placeholders


@dataclass
class BoolNode(Node):
    value: bool


@dataclass
class NoneNode(Node):
    pass


@dataclass
class VarNode(Node):
    name: str


@dataclass
class IndexNode(Node):
    collection: 'Node'
    index: 'Node'


@dataclass
class ListNode(Node):
    elements: List['Node']


@dataclass
class ListAppendNode(Node):
    name: str
    value: 'Node'


@dataclass
class ListPopNode(Node):
    name: str
    index: 'Node'


@dataclass
class AugAssignNode(Node):
    name: str
    op: str           # '+=' or '-='
    value: 'Node'


@dataclass
class CastNode(Node):
    cast_type: str    # 'int', 'float', 'str'
    value: 'Node'


@dataclass
class RandomNode(Node):
    low: 'Node'
    high: 'Node'


@dataclass
class LenNode(Node):
    value: 'Node'


@dataclass
class ExitNode(Node):
    pass


@dataclass
class HttpGetNode(Node):
    url: 'Node'


@dataclass
class HttpPostNode(Node):
    url: 'Node'
    body: 'Node'
