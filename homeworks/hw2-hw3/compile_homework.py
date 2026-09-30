#!/usr/bin/env python3
import re
from pathlib import Path

HERE = Path(__file__).parent
OUTPUT = HERE / "compiled-homework.md"

IMAGE_CAPTIONS = {
    "problem.png": "Условие",
    "solution.png": "Решение",
    "nfa.png": "НКА",
    "dfa.png": "ДКА",
    "min.png": "Минимальный ДКА",
    "original-min.png": "МДКА исходного языка",
    "complement-min.png": "МДКА дополнения (complement)",
    "answer-min.png": "МДКА полученного ответа",
}
IMAGE_ORDER = [
    "solution.png",
    "nfa.png",
    "dfa.png",
    "min.png",
    "original-min.png",
    "complement-min.png",
    "answer-min.png",
]


def task_number(path: Path) -> int:
    return int(re.match(r"task(\d+)", path.name).group(1))


def shift_headings(markdown: str, levels: int) -> str:
    def repl(match: re.Match) -> str:
        return "#" * (len(match.group(1)) + levels) + match.group(2)

    return re.sub(r"^(#+)( .*)$", repl, markdown, flags=re.MULTILINE)


def image_block(unit_dir: Path, filename: str) -> str:
    rel_path = unit_dir.relative_to(HERE) / filename
    caption = IMAGE_CAPTIONS.get(filename)
    line = f"![{caption or filename}]({rel_path})"
    if caption:
        line += f"\n\n*{caption}.*"
    return line


def render_unit(unit_dir: Path, heading_level: int) -> list[str]:
    parts: list[str] = []

    if (unit_dir / "problem.png").exists():
        parts.append(image_block(unit_dir, "problem.png"))

    solution_md = unit_dir / "solution.md"
    if solution_md.exists():
        parts.append(shift_headings(solution_md.read_text().strip(), heading_level + 1))
    elif not any((unit_dir / name).exists() for name in IMAGE_ORDER):
        parts.append("_Решение отсутствует._")

    for name in IMAGE_ORDER:
        if (unit_dir / name).exists():
            parts.append(image_block(unit_dir, name))

    return parts


def render_task(task_dir: Path) -> list[str]:
    sections = [f"## Задача {task_number(task_dir)}"]
    subparts = sorted(p for p in task_dir.iterdir() if p.is_dir())

    if subparts:
        for part_dir in subparts:
            sections.append(f"### Пункт {part_dir.name})")
            sections.extend(render_unit(part_dir, heading_level=2))
    else:
        sections.extend(render_unit(task_dir, heading_level=1))

    return sections


def main() -> None:
    task_dirs = sorted(
        (p for p in HERE.iterdir() if p.is_dir() and re.match(r"task\d+$", p.name)),
        key=task_number,
    )

    sections = [
        "# Домашнее задание 2 и 3",
        "_Теория формальных языков, ФПМИ МФТИ. Собрано автоматически скриптом compile_homework.py - правки вносить в исходные taskN/.../solution.md, а не в этот файл._",
    ]
    for task_dir in task_dirs:
        sections.extend(render_task(task_dir))

    OUTPUT.write_text("\n\n".join(sections) + "\n")
    print(f"wrote {OUTPUT.relative_to(HERE.parent.parent)}")


if __name__ == "__main__":
    main()
