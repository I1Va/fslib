import itertools

from fslib.regex.ast import Concat, Epsilon, Literal, Plus, RegexNode, Star, Union, Wildcard


def ast_to_dot(node: RegexNode) -> str:
    lines = ["digraph AST {", '    node [shape=circle, fontname="monospace"];']
    counter = itertools.count()

    def add(n: RegexNode) -> str:
        node_id = f"n{next(counter)}"
        lines.append(f'    {node_id} [label="{_label(n)}"];')
        for child in _children(n):
            child_id = add(child)
            lines.append(f"    {node_id} -> {child_id};")
        return node_id

    add(node)
    lines.append("}")
    return "\n".join(lines)


def render(dot_source: str, outfile: str) -> str:
    import graphviz

    return graphviz.Source(dot_source).render(outfile=outfile, cleanup=True)


def _label(node: RegexNode) -> str:
    if isinstance(node, Literal):
        return _escape(node.char)
    if isinstance(node, Epsilon):
        return "ε"  # epsilon
    if isinstance(node, Wildcard):
        return "."
    if isinstance(node, Concat):
        return "·"  # concatenation
    if isinstance(node, Union):
        return "|"
    if isinstance(node, Star):
        return "*"
    if isinstance(node, Plus):
        return "+"
    raise TypeError(f"unknown AST node type: {type(node).__name__}")


def _children(node: RegexNode) -> list[RegexNode]:
    if isinstance(node, (Concat, Union)):
        return [node.left, node.right]
    if isinstance(node, (Star, Plus)):
        return [node.child]
    return []


def _escape(char: str) -> str:
    return char.replace("\\", "\\\\").replace('"', '\\"')
