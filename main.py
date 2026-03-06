#!/usr/bin/env python3
# main.py — Точка входа интерпретатора языка ПОВЕЛЕВАЮ
# Запуск:  python main.py program.pov
# Отладка: python main.py program.pov --debug
# REPL:    python main.py --repl

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import PovelError


BANNER = """
╔══════════════════════════════════════════════════════╗
║         ПОВЕЛЕВАЮ — Язык Древней Руси v1.0           ║
║     Введите 'выход' или 'почить' для завершения       ║
╚══════════════════════════════════════════════════════╝
"""


def run_source(source: str, debug: bool = False, current_file: str | None = None) -> bool:
    """Запускает исходный код. Возвращает True при успехе."""
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        if debug:
            print("[ОТЛАДКА] Токены:")
            for tok in tokens:
                print(f"  {tok}")
            print()

        parser = Parser(tokens)
        ast = parser.parse()

        if debug:
            print("[ОТЛАДКА] AST:")
            _print_ast(ast, indent=2)
            print()

        interp = Interpreter(debug=debug, current_file=current_file)
        interp.execute(ast)
        return True

    except PovelError as e:
        print(f"\n{e}\n", file=sys.stderr)
        return False
    except SystemExit:
        raise
    except KeyboardInterrupt:
        print("\n\n— Прерванo волею пользователя. —")
        return False
    except Exception as e:
        print(f"\n⚔ Беда непредвиденная: {type(e).__name__}: {e}\n", file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        return False


def run_repl():
    """REPL-режим: интерактивная консоль языка ПОВЕЛЕВАЮ"""
    print(BANNER)
    print("Вводите команды на языке ПОВЕЛЕВАЮ. Пустая строка — выполнить.\n")

    from interpreter import Interpreter, Environment
    from lexer import Lexer
    from parser import Parser
    from errors import PovelError

    interp = Interpreter()
    buffer = []

    def try_exec(lines):
        source = '\n'.join(lines)
        if not source.strip():
            return
        # Добавляем заголовок и конец если нет
        if not source.strip().startswith('Свиток'):
            source = 'Свиток REPL "Диалог"\n' + source
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            for stmt in ast.body:
                interp.execute(stmt)
        except PovelError as e:
            print(f"{e}")
        except SystemExit:
            raise
        except Exception as e:
            print(f"⚔ Беда: {e}")

    while True:
        try:
            if buffer:
                line = input("... ")
            else:
                line = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print("\n— Прощай! —")
            break

        if line.strip().lower() in ('выход', 'почить', 'exit', 'quit'):
            print("— Прощай! —")
            break

        if line == '' and buffer:
            try_exec(buffer)
            buffer = []
        elif line != '':
            buffer.append(line)


def _print_ast(node, indent=0):
    """Красивая печать AST для отладки"""
    prefix = ' ' * indent
    node_type = type(node).__name__
    if hasattr(node, '__dataclass_fields__'):
        print(f"{prefix}{node_type}:")
        for field_name, _ in node.__dataclass_fields__.items():
            if field_name == 'line':
                continue
            val = getattr(node, field_name)
            if isinstance(val, list):
                print(f"{prefix}  {field_name}:")
                for item in val:
                    if hasattr(item, '__dataclass_fields__'):
                        _print_ast(item, indent + 4)
                    elif isinstance(item, tuple):
                        print(f"{prefix}    branch:")
                        cond, body = item
                        if cond:
                            _print_ast(cond, indent + 6)
                        else:
                            print(f"{prefix}      else")
                        for s in body:
                            _print_ast(s, indent + 6)
                    else:
                        print(f"{prefix}    {item!r}")
            elif hasattr(val, '__dataclass_fields__'):
                print(f"{prefix}  {field_name}:")
                _print_ast(val, indent + 4)
            else:
                print(f"{prefix}  {field_name}: {val!r}")
    else:
        print(f"{prefix}{node!r}")


def main():
    args = sys.argv[1:]

    if not args or '--repl' in args:
        run_repl()
        return

    debug = '--debug' in args
    files = [a for a in args if not a.startswith('--')]

    if not files:
        print("Использование: python main.py <файл.pov> [--debug]")
        print("              python main.py --repl")
        sys.exit(1)

    filepath = files[0]
    if not os.path.exists(filepath):
        print(f"⚔ Свиток не найден: '{filepath}'", file=sys.stderr)
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    success = run_source(source, debug=debug, current_file=filepath)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
