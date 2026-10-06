# fslib
Небольшая библиотека для работы с регулярными выражениями и конечными
автоматами.

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,viz]"
```

## Использование: regex -> FSM -> детерминизация -> минимизация

```python
from fslib.regex.parser import parse
from fslib.passes.construct import thompson
from fslib.passes.determinize import determinize
from fslib.passes.minimize import minimize

pattern = "a(b|c)*"

ast = parse(pattern)              # regex -> AST
nfa = thompson(ast)               # AST -> FSM 
dfa = determinize(nfa)            # FSM -> детерминированный FSM
min_dfa = minimize(dfa)           # детерминированный FSM -> минимальный FSM 

assert nfa.accepts("abcbc") == dfa.accepts("abcbc") == min_dfa.accepts("abcbc")
print(min_dfa.accepts("abcbc"))   # True
print(min_dfa.accepts("abd"))     # False
```

## Построение МПДКА из регулярного выражения

Да, библиотека строит именно **минимальный полный** ДКА: `minimize` сам по себе требует полный
автомат на входе, а `determinize` всегда выдаёт полный (недостающие переходы ведут в сток, который
появляется как пустое подмножество). Поэтому результат `min` — это МПДКА, а не просто МДКА.

Одной командой:

```bash
fslib min "(b(a|b)a*)+(ba)*ba+" --out mpdka.png
```

Тот же конвейер по шагам:

```python
from fslib.regex.parser import parse
from fslib.passes.construct import thompson
from fslib.passes.determinize import determinize
from fslib.passes.minimize import minimize

ast = parse("(b(a|b)a*)+(ba)*ba+")  # 1. разбор регулярки в AST
nfa = thompson(ast)                 # 2. алгоритм Томпсона: AST -> НКА с eps-переходами
                                    #    (сразу стягивает лишние eps-рёбра)
dfa = determinize(nfa)              # 3. построение подмножеств: НКА -> полный ДКА (со стоком)
mpdka = minimize(dfa)               # 4. алгоритм Хопкрофта: склейка эквивалентных состояний
```

### Синтаксис регулярок

| Запись | Значение |
|---|---|
| `\|` | объединение |
| `*` | звезда Клини, ноль или более |
| `+` | плюс Клини, одно или более (постфиксный) |
| `.` | любой символ алфавита |
| `\` | экранирование: `\*` — литерал `*`, `\ ` — литерал пробела |

Пробелы и табуляции незначащие, их можно ставить для читаемости: `a | b` и `a|b` — одно и то же.
Чтобы получить пробел как символ языка, экранируйте его: `a\ b` задаёт слово `a b`.

### Внимание: `+` — это НЕ объединение

В учебных конспектах объединение обычно пишут знаком `+`: $a + b$. **Здесь так нельзя.** В этой
библиотеке `+` всегда означает плюс Клини, независимо от пробелов вокруг, и `a + b` молча разберётся
как $a^{+}b$ — ошибки не будет, просто получится другой язык. Объединение всегда пишется через `|`.

Перевод из конспекта в синтаксис библиотеки:

| В конспекте | Здесь | Комментарий |
|---|---|---|
| $a + b$ | `a\|b` | объединение |
| $a^{+}$ | `a+` | плюс Клини, пишется так же |
| $a^{*}$ | `a*` | звезда, пишется так же |
| $(a+b)^2$ | `(a\|b)(a\|b)` | степеней в синтаксисе нет, раскрывайте в конкатенацию |
| $\varepsilon$, $1$ | пустая альтернатива: `(\|a)` | это «пусто или `a`» |

Например, $\;(b(a + b)a^*)^{+}(ba)^*ba^{+}$ записывается как `(b(a|b)a*)+(ba)*ba+`.

### Алфавит

По умолчанию алфавит выводится из литералов самой регулярки. Если нужный алфавит шире, задайте его
явно — это важно для `.` и критично для дополнения, которое по определению зависит от Σ:

```bash
fslib min "a*" --alphabet ab          # сток по букве b появится только с этим флагом
fslib complement "a*" --alphabet ab   # дополнение над Σ={a,b}, а не над Σ={a}
```

## Дополнение языка

`complement` принимает **любой** автомат: если он недетерминирован или неполон, детерминизация
выполняется сама. Дополнение берётся относительно алфавита автомата, поэтому почти всегда нужен
явный `--alphabet` — иначе для `a*` получится Σ={a} и слова с `b` не попадут в дополнение.

```bash
fslib complement "a*" --alphabet ab --out co.png   # автомат дополнения
fslib complement-regex "a*" --alphabet ab          # a*b(a|b)*
```

```python
from fslib.passes import complement, determinize, minimize, thompson
from fslib.regex.parser import parse

nfa = thompson(parse("a*"), frozenset("ab"))
co = minimize(complement(nfa))          # complement сам детерминизирует
assert co.accepts("b") and not co.accepts("aaa")
```

## Регулярка из автомата

`fsm_to_regex` строит регулярное выражение по автомату методом исключения состояний: автомат
достраивается до GNFA, затем состояния по одному выбрасываются, а метки рёбер склеиваются по правилу
$R(p,q) \cup R(p,k)R(k,k)^*R(k,q)$. Порядок исключения выбирается жадно (сначала состояния с
наименьшим произведением входящей и исходящей степени), а упрощения $\varnothing r = \varnothing$,
$\varepsilon r = r$, $\varnothing^* = \varepsilon$ применяются на лету — без них выражение разрастается.

```bash
fslib regex "a**"           # a*
fslib regex "(a|a)(b|b)"    # ab
```

```python
from fslib.passes import determinize, fsm_to_regex, minimize, thompson
from fslib.regex.parser import parse

mpdka = minimize(determinize(thompson(parse("(a|b)*abb"))))
node = fsm_to_regex(mpdka)   # обратно в AST
print(node.pattern())        # b*aa*b((a|b(a|bb*a))a*b)*b
```

Метод `pattern()` печатает любой AST обратно в строку (расставляя скобки и экранирование), так что
`parse(node.pattern()) == node`. Для пустого языка выражения не существует — в этом синтаксисе нет
обозначения для $\varnothing$, поэтому `fsm_to_regex` поднимает `ValueError`.

## Визуализация FSM через Graphviz

```python
from fslib.viz import fsm_to_dot, render

dot_source = fsm_to_dot(min_dfa)
render(dot_source, "min.png")    
```

## То же самое из командной строки

```bash
fslib parse "a(b|c)*"                        # AST
fslib tree "a(b|c)*" --out ast.png           # картинка AST
fslib automaton "a(b|c)*" --out nfa.png      # НКА (Томпсон)
fslib dfa "a(b|c)*" --out dfa.png            # полный ДКА
fslib min "a(b|c)*" --out min.png            # МПДКА
fslib complement "a(b|c)*" --out co.png      # МПДКА дополнения
fslib regex "a**"                            # регулярка из автомата (упрощение)
fslib complement-regex "a*" --alphabet ab    # регулярка для дополнения
fslib match "a(b|c)*" abcbc                  # проверка принадлежности
```

Команды, строящие автомат, принимают необязательный `--alphabet` (см. ниже).

## Запуск тестов и проверка покрытия

```bash
# все тесты
pytest

# с отчётом о покрытии
pytest --cov=fslib --cov-report=term-missing
```

