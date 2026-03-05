# ПОВЕЛЕВАЮ

Интерпретатор учебного языка «ПОВЕЛЕВАЮ» на Python 3.10+.

## Запуск

```bash
python main.py poveleyayu/examples/hello.pov
python main.py poveleyayu/examples/ugadai_chislo.pov
python main.py --repl
python main.py poveleyayu/examples/hello.pov --debug
```

## Структура

- `poveleyayu/lexer.py` — ручной построчный лексер с контролем отступов.
- `poveleyayu/parser.py` — recursive descent-парсер в AST.
- `poveleyayu/nodes.py` — AST-узлы.
- `poveleyayu/interpreter.py` — visitor-интерпретатор со scope stack.
- `poveleyayu/errors.py` — древнерусские сообщения ошибок.
- `poveleyayu/stdlib.py` — базовые функции стандартной библиотеки.
- `poveleyayu/examples/*.pov` — примеры программ.

## Поддерживаемый синтаксис

- Заголовок свитка: `Свиток ...` и финал `Повелеваю: Начать выполнение!`
- Присваивание, ввод, вывод
- Условия `Суд вершу` / `Коль` / `Иначе коль` / `Иначе`
- Циклы `Коловрат`, `Коловрат покуда`, `Странствие ...`
- Функции: `Умение нарекаю ...`, `Призвать умение ...`, `Повелеваю: Вернуть ...`
- Списки: создание, append/pop, индексирование
- Арифметика и логика в древнерусской форме
- Стандартные конструкции:
  - `из палат случайных призвать число от A до B`
  - `длина дружины Имя`
  - `оборотить ... в Число Цельное/Дробное/Слово`
- Булевы: `Зрю истину`, `Зрю ложь`, `ничто`

## Тесты

```bash
python -m unittest
```
