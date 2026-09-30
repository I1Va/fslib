## Идея
Разбиваем язык на объединение двух стандартных шаблонов "хотя бы $k$ вхождений буквы":
$$L=L_1\cup L_2,\qquad L_1=\{w:|w|_a\ge2\},\quad L_2=\{w:|w|_b\ge3\}$$

## Регулярка

```
.*a.*a.*|.*b.*b.*b.*
```

## Построение НКА

```
fslib automaton ".*a.*a.*|.*b.*b.*b.*" --out homeworks/hw2-hw3/task2/b/nfa.png
```

## Построение ДКА

```
fslib dfa ".*a.*a.*|.*b.*b.*b.*" --out homeworks/hw2-hw3/task2/b/dfa.png
```

## Построение МДКА

```
fslib min ".*a.*a.*|.*b.*b.*b.*" --out homeworks/hw2-hw3/task2/b/min.png
```