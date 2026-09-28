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

## Визуализация FSM через Graphviz

```python
from fslib.viz import fsm_to_dot, render

dot_source = fsm_to_dot(min_dfa)
render(dot_source, "min.png")    
```

## То же самое из командной строки

```bash
fslib parse "a(b|c)*"                    
fslib automaton "a(b|c)*" --out nfa.png  
fslib dfa "a(b|c)*" --out dfa.png       
fslib min "a(b|c)*" --out min.png        
fslib match "a(b|c)*" abcbc              
```

## Запуск тестов и проверка покрытия

```bash
# все тесты
pytest

# с отчётом о покрытии
pytest --cov=fslib --cov-report=term-missing
```

