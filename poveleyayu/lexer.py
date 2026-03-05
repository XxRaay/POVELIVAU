from dataclasses import dataclass

from .errors import LexerError


@dataclass
class Token:
    kind: str
    value: str
    line: int
    indent: int = 0


class Lexer:
    def tokenize(self, source: str) -> list[Token]:
        tokens: list[Token] = []
        for i, raw_line in enumerate(source.splitlines(), start=1):
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue
            indent = self._calc_indent(line, i)
            stripped = line.lstrip(" \t")
            if stripped.startswith("//"):
                continue
            body = self._remove_inline_comment(stripped)
            if body.strip():
                tokens.append(Token("LINE", body.strip(), i, indent))
        return tokens

    def _calc_indent(self, line: str, line_no: int) -> int:
        i = 0
        units = 0
        while i < len(line) and line[i] in " \t":
            if line[i] == "\t":
                units += 1
                i += 1
            else:
                count = 0
                while i < len(line) and line[i] == " ":
                    count += 1
                    i += 1
                if count % 5 != 0:
                    raise LexerError(line_no, "отступ")
                units += count // 5
        return units

    def _remove_inline_comment(self, text: str) -> str:
        in_string = False
        out = []
        for idx, ch in enumerate(text):
            if ch == '"':
                in_string = not in_string
            if not in_string and ch == "/" and idx + 1 < len(text) and text[idx + 1] == "/":
                break
            out.append(ch)
        return "".join(out)
