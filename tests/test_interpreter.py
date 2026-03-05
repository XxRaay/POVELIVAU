import io
import unittest
from contextlib import redirect_stdout

from poveleyayu.main import run_source


class InterpreterTests(unittest.TestCase):
    def run_program(self, source: str) -> str:
        out = io.StringIO()
        with redirect_stdout(out):
            run_source(source)
        return out.getvalue().strip()

    def test_hello(self):
        source = '''Свиток Сказа "Тест"
Глаголю народу: "Привет",
Повелеваю: Начать выполнение!
'''
        self.assertEqual(self.run_program(source), "Привет")

    def test_math_assign(self):
        source = '''Свиток Сказа "Тест"
Повелеваю: Отныне 2 сложить с 3 именоваться Сумма,
Вещаю: "[Сумма]",
Повелеваю: Начать выполнение!
'''
        self.assertEqual(self.run_program(source), "5")

    def test_if(self):
        source = '''Свиток Сказа "Тест"
Повелеваю: Отныне 10 именоваться X,
Суд вершу:
     Коль X больше 5:
          Вещаю: "ok",
     Иначе:
          Вещаю: "bad",
Повелеваю: Начать выполнение!
'''
        self.assertEqual(self.run_program(source), "ok")


if __name__ == "__main__":
    unittest.main()
