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
class PrintLinesNode(Node):
    """Построчный вывод элементов дружины (списка)."""
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


@dataclass
class ListDirNode(Node):
    """Получить список содержимого текущей земли (os.listdir)."""
    pass


@dataclass
class CwdNode(Node):
    """Получить путь текущей земли (os.getcwd)."""
    pass


@dataclass
class PathExistsNode(Node):
    """Проверить, что путь существует в землях (os.path.exists)."""
    path: 'Node'


@dataclass
class ChdirNode(Node):
    """Сменить текущую землю (os.chdir)."""
    path: 'Node'


@dataclass
class MkdirNode(Node):
    """Возвести новый чертог (os.mkdir)."""
    path: 'Node'


@dataclass
class RmtreeNode(Node):
    """Предать забвению чертог со всеми свитками (shutil.rmtree)."""
    path: 'Node'


@dataclass
class RemoveNode(Node):
    """Изгнать свиток из земель (os.remove)."""
    path: 'Node'


@dataclass
class RenameNode(Node):
    """Переименовать грамоту (os.rename)."""
    src: 'Node'
    dst: 'Node'


@dataclass
class FileWriteNode(Node):
    """Вписать строку в свиток (файл)."""
    path: 'Node'
    text: 'Node'


@dataclass
class FileReadLinesNode(Node):
    """Прочитать свиток (файл) и вернуть дружину строк."""
    path: 'Node'


@dataclass
class FileDeleteLineNode(Node):
    """Вычеркнуть строку из свитка (файл) по номеру (1 = первая)."""
    path: 'Node'
    line_no: 'Node'


@dataclass
class FileCreateNode(Node):
    """Сотворить новый пустой свиток (файл)."""
    path: 'Node'
