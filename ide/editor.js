/* ════════════════════════════════════════════════════════
   ПОВЕЛЕВАЮ IDE — editor.js
   Подсветка синтаксиса, автодополнение, запуск программ
   ════════════════════════════════════════════════════════ */

// ══════════════════════════════════════════════════════════
//  ДАННЫЕ ЯЗЫКА
// ══════════════════════════════════════════════════════════

const KEYWORDS = [
  "Повелеваю: Взять слово от гостя заезжего, оборотить его в Число Цельное и наречь",
  "Повелеваю: Взять слово от гостя заезжего, оборотить его в Число Дробное и наречь",
  "Повелеваю: Взять слово от гостя заезжего и наречь",
  "Указываю: Сотворить сундук пустой, именем",
  "из палат случайных призвать число от",
  "Повелеваю: Остановить всё и почить",
  "Повелеваю: Пресечь бег сего коловрата",
  "Повелеваю: Перейти к следующему витку",
  "Повелеваю: Начать выполнение!",
  "остаток от деления на",
  "Изгнать из дружины",
  "Убавить из сундука",
  "Ратник под номером",
  "Добавить в сундук",
  "Принять в дружину",
  "ратника с позиции",
  "Кричу на всю Русь:",
  "Повелеваю: Вернуть",
  "Повелеваю: Отныне",
  "и положить в него",
  "Умение нарекаю",
  "Призвать умение",
  "Глаголю народу:",
  "Дружина именем",
  "по землям от",
  "Коловрат покуда",
  "длина дружины",
  "в точности как",
  "и к тому же",
  "Зрю истину",
  "Иначе коль",
  "Вопрошаю гостя:",
  "Суд вершу:",
  "Коловрат:",
  "Зрю ложь",
  "сложить с",
  "умножить на",
  "разделить на",
  "не меньше",
  "не больше",
  "по дружине",
  "с ратниками",
  "в дружине",
  "Коловрат",
  "в Число Цельное",
  "в Число Дробное",
  "оборотить",
  "Вещаю:",
  "именоваться",
  "и наречь",
  "ратника",
  "либо же",
  "в Слово",
  "не ровня",
  "не есть",
  "Иначе:",
  "Странствие",
  "единицу малую",
  "меньше",
  "больше",
  "отнять",
  "Иначе",
  "Свиток",
  "Коль",
  "ничто",
  "до",
  "по",
  "именем",
  "единицу",
].sort((a, b) => b.length - a.length);

const COMPLETIONS = [
  { text: "Свиток",                                desc: "Заголовок программы" },
  { text: "Глаголю народу:",                       desc: "print()" },
  { text: "Вещаю:",                                desc: "print()" },
  { text: "Кричу на всю Русь:",                    desc: "print()" },
  { text: "Повелеваю: Отныне",                     desc: "Присвоить переменную" },
  { text: "Указываю: Сотворить сундук пустой, именем", desc: "Создать переменную" },
  { text: "Повелеваю: Взять слово от гостя заезжего и наречь", desc: "input() → str" },
  { text: "Повелеваю: Взять слово от гостя заезжего, оборотить его в Число Цельное и наречь", desc: "input() → int" },
  { text: "Вопрошаю гостя:",                       desc: "input(prompt)" },
  { text: "Суд вершу:",                            desc: "if / elif / else" },
  { text: "Коль",                                  desc: "if" },
  { text: "Иначе коль",                            desc: "elif" },
  { text: "Иначе:",                                desc: "else" },
  { text: "Коловрат:",                             desc: "while True:" },
  { text: "Коловрат покуда",                       desc: "while условие:" },
  { text: "Странствие",                            desc: "for" },
  { text: "по землям от",                          desc: "for в диапазоне" },
  { text: "по дружине",                            desc: "for в списке" },
  { text: "Умение нарекаю",                        desc: "def функция" },
  { text: "Призвать умение",                       desc: "вызов функции" },
  { text: "Повелеваю: Вернуть",                    desc: "return" },
  { text: "Дружина именем",                        desc: "список = []" },
  { text: "Принять в дружину",                     desc: ".append()" },
  { text: "Изгнать из дружины",                    desc: ".pop()" },
  { text: "Добавить в сундук",                     desc: "+= 1 или += N" },
  { text: "Убавить из сундука",                    desc: "-= 1" },
  { text: "из палат случайных призвать число от",  desc: "random.randint(a, b)" },
  { text: "длина дружины",                         desc: "len()" },
  { text: "оборотить",                             desc: "int/float/str()" },
  { text: "в Число Цельное",                       desc: "int()" },
  { text: "в Число Дробное",                       desc: "float()" },
  { text: "в Слово",                               desc: "str()" },
  { text: "Повелеваю: Пресечь бег сего коловрата", desc: "break" },
  { text: "Повелеваю: Перейти к следующему витку", desc: "continue" },
  { text: "Повелеваю: Остановить всё и почить",    desc: "exit()" },
  { text: "Повелеваю: Начать выполнение!",         desc: "конец программы" },
  { text: "сложить с",                             desc: "+" },
  { text: "отнять",                                desc: "-" },
  { text: "умножить на",                           desc: "*" },
  { text: "разделить на",                          desc: "/" },
  { text: "в точности как",                        desc: "==" },
  { text: "не ровня",                              desc: "!=" },
  { text: "меньше",                                desc: "<" },
  { text: "больше",                                desc: ">" },
  { text: "не меньше",                             desc: ">=" },
  { text: "не больше",                             desc: "<=" },
  { text: "и к тому же",                           desc: "and" },
  { text: "либо же",                               desc: "or" },
  { text: "не есть",                               desc: "not" },
  { text: "именоваться",                           desc: "= (конец присвоения)" },
  { text: "Зрю истину",                            desc: "True" },
  { text: "Зрю ложь",                              desc: "False" },
  { text: "ничто",                                 desc: "None" },
];

const TEMPLATES = {
  empty: {
    icon: "📜", label: "Пустой свиток",
    code: `Свиток Сказа "Без Названия"\n\n// Введите код здесь\n\nПовелеваю: Начать выполнение!`,
  },
  hello: {
    icon: "👋", label: "Приветствие",
    code:
`Свиток Сказа "Приветствие"

Вопрошаю гостя: "Как тебя зовут, странник? " и наречь Имя,
Вещаю: "Слава Руси! Приветствую тебя, [Имя]!",
Глаголю народу: "Сие есть первая программа на языке Повелеваю!",

Повелеваю: Начать выполнение!`,
  },
  calc: {
    icon: "🔢", label: "Калькулятор",
    code:
`Свиток Деяния "Калькулятор"

Глаголю народу: "╔══════════════════════╗",
Глаголю народу: "║  Великий Калькулятор  ║",
Глаголю народу: "╚══════════════════════╝",

Вопрошаю гостя: "Введи первое число: " и наречь Первое,
Повелеваю: Отныне оборотить Первое в Число Дробное именоваться Первое,

Вопрошаю гостя: "Введи второе число: " и наречь Второе,
Повелеваю: Отныне оборотить Второе в Число Дробное именоваться Второе,

Повелеваю: Отныне Первое сложить с Второе именоваться Сумма,
Повелеваю: Отныне Первое отнять Второе именоваться Разность,
Повелеваю: Отныне Первое умножить на Второе именоваться Произведение,

Вещаю: "Сложить:   [Сумма]",
Вещаю: "Отнять:    [Разность]",
Вещаю: "Умножить:  [Произведение]",

Суд вершу:
     Коль Второе не ровня 0:
           Повелеваю: Отныне Первое разделить на Второе именоваться Частное,
           Вещаю: "Разделить: [Частное]",
     Иначе:
           Вещаю: "Делить на нуль — грех великий!",

Повелеваю: Начать выполнение!`,
  },
  game: {
    icon: "🎲", label: "Угадай число",
    code:
`Свиток Забавы "Тайное Число"

Повелеваю: Отныне из палат случайных призвать число от 1 до 100 именоваться Загадка,
Указываю: Сотворить сундук пустой, именем Попытки, и положить в него 0,

Глаголю народу: "═══════════════════════════════════",
Глаголю народу: "  Добро пожаловать в Тайное Число!",
Глаголю народу: "═══════════════════════════════════",

Коловрат:
     Вопрошаю гостя: "Угадай число от 1 до 100: " и наречь Догадка,
     Повелеваю: Отныне оборотить Догадка в Число Цельное именоваться Догадка,
     Добавить в сундук Попытки единицу малую,

     Суд вершу:
           Коль Догадка в точности как Загадка:
                 Вещаю: "Победа! Угадал за [Попытки] попыток!",
                 Повелеваю: Пресечь бег сего коловрата,
           Иначе коль Догадка меньше Загадка:
                 Вещаю: "Бери выше!",
           Иначе:
                 Вещаю: "Бери ниже!",

Повелеваю: Начать выполнение!`,
  },
  func: {
    icon: "⚔",  label: "Функции и списки",
    code:
`Свиток Деяния "Дружина и Умения"

// Функция: сумма списка
Умение нарекаю СуммаДружины(Дружина):
     Указываю: Сотворить сундук пустой, именем Итог, и положить в него 0,
     Странствие Ратник по дружине Дружина:
           Повелеваю: Отныне Итог сложить с Ратник именоваться Итог,
     Повелеваю: Вернуть Итог,

Дружина именем Числа с ратниками [10, 20, 30, 40, 50],
Повелеваю: Отныне Призвать умение СуммаДружины(Числа) именоваться Сумма,
Вещаю: "Сумма ратников: [Сумма]",

Принять в дружину Числа ратника 60,
Повелеваю: Отныне длина дружины Числа именоваться Размер,
Вещаю: "Дружина пополнена. Размер: [Размер]",

Глаголю народу: "Таблица умножения на 7:",
Странствие И по землям от 1 до 10:
     Повелеваю: Отныне И умножить на 7 именоваться Результат,
     Вещаю: "[И] × 7 = [Результат]",

Повелеваю: Начать выполнение!`,
  },
};

// ══════════════════════════════════════════════════════════
//  ПОДСВЕТКА СИНТАКСИСА
// ══════════════════════════════════════════════════════════

function escHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function highlightLine(line) {
  const out = [];
  let pos = 0;

  while (pos < line.length) {
    // Пробелы/табы
    const wsM = line.slice(pos).match(/^[ \t]+/);
    if (wsM) { out.push(escHtml(wsM[0])); pos += wsM[0].length; continue; }

    // Комментарий
    if (line.slice(pos, pos + 2) === "//") {
      out.push(`<span class="hl-comment">${escHtml(line.slice(pos))}</span>`);
      break;
    }

    // Строка
    if (line[pos] === '"') {
      const end = line.indexOf('"', pos + 1);
      const raw = end !== -1 ? line.slice(pos, end + 1) : line.slice(pos);
      const inner = escHtml(raw.slice(1, end !== -1 ? raw.length - 1 : undefined))
        .replace(/\[([А-ЯЁа-яёA-Za-z_][А-ЯЁа-яёA-Za-z0-9_]*)\]/g,
          '<span class="hl-interp">[$1]</span>');
      out.push(`<span class="hl-str">"${inner}${end !== -1 ? '"' : ''}</span>`);
      pos += raw.length; continue;
    }

    // Число
    const numM = line.slice(pos).match(/^\d+(\.\d+)?/);
    if (numM) {
      out.push(`<span class="hl-num">${numM[0]}</span>`);
      pos += numM[0].length; continue;
    }

    // Ключевые слова (от длинных к коротким)
    let hit = false;
    for (const kw of KEYWORDS) {
      if (line.slice(pos).startsWith(kw)) {
        const after = line[pos + kw.length];
        if (after === undefined || !/[А-ЯЁа-яёA-Za-z0-9_]/.test(after)) {
          out.push(`<span class="hl-kw">${escHtml(kw)}</span>`);
          pos += kw.length; hit = true; break;
        }
      }
    }
    if (hit) continue;

    // Идентификатор
    const idM = line.slice(pos).match(/^[А-ЯЁа-яёA-Za-z_][А-ЯЁа-яёA-Za-z0-9_]*/);
    if (idM) {
      const cls = /^[А-ЯЁA-Z]/.test(idM[0]) ? "hl-var" : "hl-ident";
      out.push(`<span class="${cls}">${escHtml(idM[0])}</span>`);
      pos += idM[0].length; continue;
    }

    // Прочие символы
    out.push(`<span class="hl-punct">${escHtml(line[pos])}</span>`);
    pos++;
  }
  return out.join("") || " ";
}

function highlight(code) {
  return code.split("\n").map(highlightLine).join("\n");
}

// ══════════════════════════════════════════════════════════
//  РЕДАКТОР
// ══════════════════════════════════════════════════════════

const ta        = document.getElementById("code-input");
const overlay   = document.getElementById("highlight-overlay");
const lineNums  = document.getElementById("line-numbers");
const acPopup   = document.getElementById("ac-popup");
const acList    = document.getElementById("ac-list");

let acVisible   = false;
let acItems     = [];
let acIndex     = 0;

// ── Инициализация ──────────────────────────────────────
function init() {
  setCode(TEMPLATES.hello.code);
  bindEvents();
  buildTemplateGrid();
}

function setCode(code) {
  ta.value = code;
  updateHighlight();
  updateLineNumbers();
}

// ── Синхронизация скролла ───────────────────────────────
function syncScroll() {
  overlay.scrollTop  = ta.scrollTop;
  overlay.scrollLeft = ta.scrollLeft;
  lineNums.scrollTop = ta.scrollTop;
}

// ── Обновление подсветки ────────────────────────────────
function updateHighlight() {
  overlay.innerHTML = highlight(ta.value);
}

// ── Обновление номеров строк ────────────────────────────
function updateLineNumbers() {
  const count = ta.value.split("\n").length;
  // Только если изменилось количество
  const cur = lineNums.children.length;
  if (cur === count) return;
  if (cur < count) {
    for (let i = cur + 1; i <= count; i++) {
      const d = document.createElement("div");
      d.className = "line-num";
      d.textContent = i;
      lineNums.appendChild(d);
    }
  } else {
    while (lineNums.children.length > count)
      lineNums.removeChild(lineNums.lastChild);
  }
}

// ══════════════════════════════════════════════════════════
//  АВТОДОПОЛНЕНИЕ
// ══════════════════════════════════════════════════════════

function getLineUpToCursor() {
  const pos = ta.selectionStart;
  const last = ta.value.lastIndexOf("\n", pos - 1);
  return ta.value.substring(last + 1, pos);
}

function showAC() {
  const lineUp = getLineUpToCursor().trimStart();
  if (lineUp.length < 2) { hideAC(); return; }

  const matches = COMPLETIONS.filter(c =>
    c.text.toLowerCase().startsWith(lineUp.toLowerCase())
  ).slice(0, 9);

  if (!matches.length) { hideAC(); return; }

  acItems = matches;
  acIndex = 0;
  renderAC();

  // Позиционируем попап под текущей строкой
  const pos = ta.selectionStart;
  const textBefore = ta.value.substring(0, pos);
  const lineNum = (textBefore.match(/\n/g) || []).length;
  const lineH   = parseFloat(getComputedStyle(ta).fontSize) * 1.6;
  const pad     = 16;
  const topPx   = lineNum * lineH + pad + lineH - ta.scrollTop;

  acPopup.style.top     = topPx + "px";
  acPopup.style.left    = pad + "px";
  acPopup.style.display = "flex";
  acVisible = true;
}

function renderAC() {
  acList.innerHTML = "";
  acItems.forEach((item, i) => {
    const div = document.createElement("div");
    div.className = "ac-item" + (i === acIndex ? " active" : "");
    div.innerHTML =
      `<span class="ac-text">${escHtml(item.text)}</span>` +
      `<span class="ac-desc">${escHtml(item.desc)}</span>`;
    div.addEventListener("mousedown", e => { e.preventDefault(); applyAC(i); });
    acList.appendChild(div);
  });
}

function hideAC() {
  acPopup.style.display = "none";
  acVisible = false;
}

function applyAC(idx) {
  const item = acItems[idx];
  const pos = ta.selectionStart;
  const lineStart = ta.value.lastIndexOf("\n", pos - 1) + 1;
  const lineUp = ta.value.substring(lineStart, pos);
  const indent = lineUp.match(/^([ \t]*)/)[1];

  const before = ta.value.slice(0, lineStart) + indent + item.text;
  const after  = ta.value.slice(pos);
  ta.value = before + after;

  const newPos = before.length;
  ta.selectionStart = ta.selectionEnd = newPos;
  updateHighlight();
  hideAC();
  ta.focus();
}

// ══════════════════════════════════════════════════════════
//  СОБЫТИЯ РЕДАКТОРА
// ══════════════════════════════════════════════════════════

function bindEvents() {
  // Ввод
  ta.addEventListener("input", () => {
    updateHighlight();
    updateLineNumbers();
    showAC();
  });

  // Скролл
  ta.addEventListener("scroll", syncScroll);

  // Клик — закрываем AC
  ta.addEventListener("click", hideAC);

  ta.addEventListener("keydown", e => {
    // Ctrl+Enter → запустить
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runCode();
      return;
    }

    // Навигация по AC
    if (acVisible) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        acIndex = Math.min(acIndex + 1, acItems.length - 1);
        renderAC(); return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        acIndex = Math.max(acIndex - 1, 0);
        renderAC(); return;
      }
      if (e.key === "Tab" || (e.key === "Enter" && acVisible)) {
        e.preventDefault();
        applyAC(acIndex);
        return;
      }
      if (e.key === "Escape") {
        hideAC(); return;
      }
    }

    // Tab → 5 пробелов
    if (e.key === "Tab") {
      e.preventDefault();
      const ss = ta.selectionStart, se = ta.selectionEnd;
      const sp = "     ";
      ta.value = ta.value.slice(0, ss) + sp + ta.value.slice(se);
      ta.selectionStart = ta.selectionEnd = ss + sp.length;
      updateHighlight();
      return;
    }

    // Enter → автоотступ + +5 пробелов после ":"
    if (e.key === "Enter") {
      e.preventDefault();
      const ss = ta.selectionStart;
      const lineStart = ta.value.lastIndexOf("\n", ss - 1) + 1;
      const curLine   = ta.value.slice(lineStart, ss);
      const indent    = curLine.match(/^([ \t]*)/)[1];
      const extra     = curLine.trimEnd().endsWith(":") ? "     " : "";

      const ins = "\n" + indent + extra;
      ta.value = ta.value.slice(0, ss) + ins + ta.value.slice(ss);
      ta.selectionStart = ta.selectionEnd = ss + ins.length;
      updateHighlight();
      updateLineNumbers();
      syncScroll();
      return;
    }

    // Любая другая — закрываем AC
    if (!["ArrowLeft","ArrowRight","Home","End","Shift"].includes(e.key)) {
      // не скрываем сразу — input event сам решит
    }
  });
}

// ══════════════════════════════════════════════════════════
//  ЗАПУСК ПРОГРАММЫ
// ══════════════════════════════════════════════════════════

async function runCode() {
  const code  = ta.value;
  const stdin = document.getElementById("stdin-input").value;

  const runBtn    = document.getElementById("btn-run");
  const runIcon   = document.getElementById("run-icon");
  const runLabel  = document.getElementById("run-label");
  const consoleOut = document.getElementById("console-out");

  // Блокируем кнопку
  runBtn.disabled = true;
  runIcon.className = "running";
  runIcon.textContent = "⏳";
  runLabel.textContent = "Исполняю...";

  setConsole("⏳ Разворачиваю свиток...", false);

  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, stdin }),
    });

    const data = await res.json();
    const isError = !!data.stderr || data.returncode !== 0;

    let output = "";
    if (data.stdout) output += data.stdout;
    if (data.stderr) output += (output ? "\n" : "") + data.stderr;
    if (!output)     output = "(Программа завершена без вывода)";

    setConsole(output, isError);

  } catch (err) {
    setConsole(
      "⚔ Не удалось связаться с сервером!\n\n" +
      "Убедись что server.py запущен:\n  python server.py\n\n" +
      `Ошибка: ${err.message}`,
      true
    );
  } finally {
    runBtn.disabled = false;
    runIcon.className = "";
    runIcon.textContent = "▶";
    runLabel.textContent = "Запустить";
  }
}

function setConsole(text, isError) {
  const co = document.getElementById("console-out");
  const ph = document.getElementById("console-placeholder");
  const clearBtn = document.getElementById("btn-clear");

  if (ph) ph.style.display = "none";
  clearBtn.style.display = "inline-block";

  let pre = document.getElementById("console-pre");
  if (!pre) {
    pre = document.createElement("pre");
    pre.id = "console-pre";
    co.appendChild(pre);
  }
  pre.className = isError ? "has-error" : "";
  pre.textContent = text;
}

// ══════════════════════════════════════════════════════════
//  ШАПКА: КНОПКИ
// ══════════════════════════════════════════════════════════

// Шаблоны
function buildTemplateGrid() {
  const grid = document.getElementById("template-grid");
  for (const [key, tpl] of Object.entries(TEMPLATES)) {
    const card = document.createElement("div");
    card.className = "tpl-card";
    card.innerHTML =
      `<div class="tpl-icon">${tpl.icon}</div>` +
      `<div class="tpl-label">${tpl.label}</div>`;
    card.addEventListener("click", () => {
      setCode(tpl.code);
      closeModal();
    });
    grid.appendChild(card);
  }
}

function openModal()  { document.getElementById("modal-overlay").style.display = "flex"; }
function closeModal() { document.getElementById("modal-overlay").style.display = "none"; }

document.getElementById("btn-templates").addEventListener("click", openModal);
document.getElementById("modal-close").addEventListener("click", closeModal);
document.getElementById("modal-overlay").addEventListener("click", e => {
  if (e.target === document.getElementById("modal-overlay")) closeModal();
});

// Открыть файл
document.getElementById("btn-open").addEventListener("click", () => {
  document.getElementById("file-input").click();
});
document.getElementById("file-input").addEventListener("change", e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    setCode(ev.target.result);
    document.getElementById("filename-text").textContent = file.name;
    document.getElementById("filename-input").value = file.name;
  };
  reader.readAsText(file, "utf-8");
  e.target.value = "";
});

// Скачать
document.getElementById("btn-download").addEventListener("click", () => {
  const name = document.getElementById("filename-input").value || "программа.pov";
  const blob = new Blob([ta.value], { type: "text/plain;charset=utf-8" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href = url;
  a.download = name.endsWith(".pov") ? name : name + ".pov";
  a.click();
  URL.revokeObjectURL(url);
});

// stdin toggle
// Запустить
document.getElementById("btn-run").addEventListener("click", runCode);

// Очистить консоль
document.getElementById("btn-clear").addEventListener("click", () => {
  const co = document.getElementById("console-out");
  co.innerHTML = `
    <div id="console-placeholder">
      <div class="ph-icon">⚜</div>
      <div class="ph-text">Нажмите <strong>▶ Запустить</strong> для исполнения свитка</div>
      <div class="ph-hint">или Ctrl+Enter</div>
    </div>`;
  document.getElementById("btn-clear").style.display = "none";
});

// ══ Имя файла: двойной клик для редактирования ══════════
const fnDisplay = document.getElementById("filename-display");
const fnInput   = document.getElementById("filename-input");
const fnText    = document.getElementById("filename-text");

fnDisplay.addEventListener("click", () => {
  fnDisplay.style.display = "none";
  fnInput.style.display   = "inline-block";
  fnInput.focus();
  fnInput.select();
});
fnInput.addEventListener("blur", commitFilename);
fnInput.addEventListener("keydown", e => {
  if (e.key === "Enter" || e.key === "Escape") commitFilename();
});
function commitFilename() {
  fnText.textContent      = fnInput.value || "программа.pov";
  fnDisplay.style.display = "inline";
  fnInput.style.display   = "none";
}

// ══ Запуск ══════════════════════════════════════════════
init();
