"""Render an AST/FSM as Graphviz output (an analysis, not a pass).

`ast_to_dot` needs nothing beyond the standard library — it just builds a
DOT-format string. `render` additionally needs the optional `graphviz`
package (and its `dot` binary) to turn that string into an image, so the
import is deferred to keep `ast_to_dot` usable without the `viz` extra.
"""

import itertools

from fslib.regex.ast import Concat, Epsilon, Literal, Plus, RegexNode, Star, Union, Wildcard


def ast_to_dot(node: RegexNode) -> str:
    """Render a regex AST as Graphviz DOT source (a parse tree)."""
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
    """Render `dot_source` to an image file at `outfile` (format inferred from its extension).

    Requires the optional `graphviz` package and a `dot` binary on PATH.
    """
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
