#!/usr/bin/env python3
# tests/test_interpreter.py — Юнит-тесты для интерпретатора ПОВЕЛЕВАЮ
import sys
import os
import io
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import PovelError, UndefinedVariableError, DivisionByZeroError


def run(source: str, inputs=None) -> str:
    """Запускает программу и возвращает вывод."""
    if not source.strip().startswith('Свиток'):
        source = 'Свиток Теста "Тест"\n' + source
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()

    captured = io.StringIO()
    input_iter = iter(inputs or [])

    with patch('builtins.print', lambda *a, **kw: captured.write(' '.join(str(x) for x in a) + '\n')):
        with patch('builtins.input', lambda *a: next(input_iter)):
            interp.execute(ast)

    return captured.getvalue().strip()


class TestBasics(unittest.TestCase):

    def test_hello_world(self):
        out = run('Глаголю народу: "Привет, мир!",')
        self.assertEqual(out, "Привет, мир!")

    def test_assign_and_print(self):
        out = run("""
Повелеваю: Отныне 42 именоваться Число,
Вещаю: "Число равно [Число]",
""")
        self.assertEqual(out, "Число равно 42")

    def test_arithmetic_add(self):
        out = run("""
Повелеваю: Отныне 10 сложить с 5 именоваться Итог,
Вещаю: "[Итог]",
""")
        self.assertEqual(out, "15")

    def test_arithmetic_sub(self):
        out = run("""
Повелеваю: Отныне 10 отнять 3 именоваться Итог,
Вещаю: "[Итог]",
""")
        self.assertEqual(out, "7")

    def test_arithmetic_mul(self):
        out = run("""
Повелеваю: Отныне 6 умножить на 7 именоваться Итог,
Вещаю: "[Итог]",
""")
        self.assertEqual(out, "42")

    def test_arithmetic_div(self):
        out = run("""
Повелеваю: Отныне 10 разделить на 4 именоваться Итог,
Вещаю: "[Итог]",
""")
        self.assertEqual(out, "2.5")

    def test_arithmetic_mod(self):
        out = run("""
Повелеваю: Отныне 10 остаток от деления на 3 именоваться Итог,
Вещаю: "[Итог]",
""")
        self.assertEqual(out, "1")

    def test_string_interpolation(self):
        out = run("""
Повелеваю: Отныне "Русь" именоваться Земля,
Глаголю народу: "Привет, [Земля]!",
""")
        self.assertEqual(out, "Привет, Русь!")


class TestConditions(unittest.TestCase):

    def test_if_true(self):
        out = run("""
Суд вершу:
     Коль 5 больше 3:
          Глаголю народу: "да",
""")
        self.assertEqual(out, "да")

    def test_if_false_else(self):
        out = run("""
Суд вершу:
     Коль 1 больше 10:
          Глаголю народу: "да",
     Иначе:
          Глаголю народу: "нет",
""")
        self.assertEqual(out, "нет")

    def test_elif(self):
        out = run("""
Повелеваю: Отныне 5 именоваться Н,
Суд вершу:
     Коль Н меньше 3:
          Глаголю народу: "мало",
     Иначе коль Н меньше 7:
          Глаголю народу: "средне",
     Иначе:
          Глаголю народу: "много",
""")
        self.assertEqual(out, "средне")

    def test_equality(self):
        out = run("""
Суд вершу:
     Коль 42 в точности как 42:
          Глаголю народу: "равно",
""")
        self.assertEqual(out, "равно")

    def test_not_equal(self):
        out = run("""
Суд вершу:
     Коль 1 не ровня 2:
          Глаголю народу: "разные",
""")
        self.assertEqual(out, "разные")


class TestLoops(unittest.TestCase):

    def test_while_with_condition(self):
        out = run("""
Указываю: Сотворить сундук пустой, именем Счёт, и положить в него 0,
Коловрат покуда Счёт меньше 3:
     Добавить в сундук Счёт единицу малую,
Вещаю: "[Счёт]",
""")
        self.assertEqual(out, "3")

    def test_while_break(self):
        out = run("""
Указываю: Сотворить сундук пустой, именем И, и положить в него 0,
Коловрат:
     Добавить в сундук И единицу малую,
     Суд вершу:
          Коль И в точности как 3:
               Повелеваю: Пресечь бег сего коловрата,
Вещаю: "[И]",
""")
        self.assertEqual(out, "3")

    def test_for_range(self):
        out = run("""
Указываю: Сотворить сундук пустой, именем Сумма, и положить в него 0,
Странствие И по землям от 1 до 5:
     Повелеваю: Отныне Сумма сложить с И именоваться Сумма,
Вещаю: "[Сумма]",
""")
        self.assertEqual(out, "15")

    def test_for_list(self):
        out = run("""
Дружина именем Д с ратниками [10, 20, 30],
Указываю: Сотворить сундук пустой, именем Итог, и положить в него 0,
Странствие Эл по дружине Д:
     Повелеваю: Отныне Итог сложить с Эл именоваться Итог,
Вещаю: "[Итог]",
""")
        self.assertEqual(out, "60")


class TestFunctions(unittest.TestCase):

    def test_simple_function(self):
        out = run("""
Умение нарекаю Удвоить(Х):
     Повелеваю: Вернуть Х умножить на 2,

Повелеваю: Отныне Призвать умение Удвоить(21) именоваться Результат,
Вещаю: "[Результат]",
""")
        self.assertEqual(out, "42")

    def test_function_with_multiple_args(self):
        out = run("""
Умение нарекаю Сложить(А, Б):
     Повелеваю: Вернуть А сложить с Б,

Повелеваю: Отныне Призвать умение Сложить(10, 32) именоваться Итог,
Вещаю: "[Итог]",
""")
        self.assertEqual(out, "42")


class TestLists(unittest.TestCase):

    def test_list_create_and_append(self):
        out = run("""
Дружина именем Д с ратниками [1, 2],
Принять в дружину Д ратника 3,
Повелеваю: Отныне длина дружины Д именоваться Дл,
Вещаю: "[Дл]",
""")
        self.assertEqual(out, "3")

    def test_list_index(self):
        out = run("""
Дружина именем Д с ратниками [10, 20, 30],
Повелеваю: Отныне Ратник под номером 1 в дружине Д именоваться Значение,
Вещаю: "[Значение]",
""")
        self.assertEqual(out, "20")


class TestErrors(unittest.TestCase):

    def test_undefined_variable(self):
        with self.assertRaises(UndefinedVariableError):
            run('Вещаю: "[НесуществующаяПеременная]",')

    def test_division_by_zero(self):
        with self.assertRaises(DivisionByZeroError):
            run("""
Повелеваю: Отныне 10 разделить на 0 именоваться Р,
""")


class TestInput(unittest.TestCase):

    def test_input_string(self):
        out = run("""
Повелеваю: Взять слово от гостя заезжего и наречь Имя,
Вещаю: "Привет, [Имя]!",
""", inputs=["Иван"])
        self.assertEqual(out, "Привет, Иван!")

    def test_input_int(self):
        out = run("""
Повелеваю: Взять слово от гостя заезжего, оборотить его в Число Цельное и наречь Число,
Повелеваю: Отныне Число умножить на 2 именоваться Удвоенное,
Вещаю: "[Удвоенное]",
""", inputs=["21"])
        self.assertEqual(out, "42")


class TestBooleans(unittest.TestCase):

    def test_true(self):
        out = run("""
Повелеваю: Отныне Зрю истину именоваться Флаг,
Суд вершу:
     Коль Флаг в точности как Зрю истину:
          Вещаю: "истина",
""")
        self.assertEqual(out, "истина")

    def test_logical_and(self):
        out = run("""
Суд вершу:
     Коль 5 больше 3 и к тому же 2 меньше 4:
          Вещаю: "оба верны",
""")
        self.assertEqual(out, "оба верны")

    def test_logical_or(self):
        out = run("""
Суд вершу:
     Коль 1 больше 10 либо же 2 меньше 4:
          Вещаю: "хоть один верен",
""")
        self.assertEqual(out, "хоть один верен")


if __name__ == '__main__':
    print("═" * 50)
    print("  Тесты языка ПОВЕЛЕВАЮ")
    print("═" * 50)
    unittest.main(verbosity=2)
