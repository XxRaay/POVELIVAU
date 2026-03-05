import argparse
from pathlib import Path

from .errors import PovelError
from .interpreter import Interpreter
from .lexer import Lexer
from .parser import Parser


def run_source(source: str, debug: bool = False):
    tokens = Lexer().tokenize(source)
    program = Parser(tokens).parse()
    if debug:
        print(program)
    Interpreter(debug=debug).run(program)


def repl():
    print("ПОВЕЛЕВАЮ REPL. Введите 'выход' для завершения.")
    interpreter = Interpreter()
    while True:
        try:
            line = input("повелеваю> ")
        except EOFError:
            break
        if line.strip().lower() == "выход":
            break
        if not line.strip():
            continue
        src = f'Свиток REPL "Живое слово"\n{line}\nПовелеваю: Начать выполнение!\n'
        try:
            tokens = Lexer().tokenize(src)
            program = Parser(tokens).parse()
            for stmt in program.body:
                interpreter.execute(stmt)
        except PovelError as e:
            print(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("program", nargs="?")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--repl", action="store_true")
    args = ap.parse_args()

    if args.repl:
        repl()
        return
    if not args.program:
        ap.error("Укажи путь к .pov свитку или --repl")
    source = Path(args.program).read_text(encoding="utf-8")
    try:
        run_source(source, debug=args.debug)
    except PovelError as e:
        print(e)


if __name__ == "__main__":
    main()
