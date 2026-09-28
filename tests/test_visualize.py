import pytest

from fslib.regex.ast import Concat, Literal, Star, Union
from fslib.regex.parser import parse
from fslib.viz import ast_to_dot, render


def test_single_literal_is_one_node():
    dot = ast_to_dot(Literal("a"))
    assert dot.startswith("digraph AST {")
    assert dot.endswith("}")
    assert 'label="a"' in dot
    assert "->" not in dot


def test_concat_has_two_children_and_one_edge_pair():
    dot = ast_to_dot(Concat(Literal("a"), Literal("b")))
    assert dot.count('label="a"') == 1
    assert dot.count('label="b"') == 1
    assert dot.count('label="·"') == 1
    assert dot.count("->") == 2


def test_union_and_star_labels():
    dot = ast_to_dot(Star(Union(Literal("a"), Literal("b"))))
    assert 'label="*"' in dot
    assert 'label="|"' in dot


def test_full_pattern_node_count_matches_ast_size():
    node = parse("a(b|c)*")
    dot = ast_to_dot(node)
    assert dot.count("[label=") == 6
    assert dot.count("->") == 5


def test_quote_and_backslash_are_escaped_in_labels():
    dot = ast_to_dot(Literal('"'))
    assert 'label="\\""' in dot
    dot = ast_to_dot(Literal("\\"))
    assert 'label="\\\\"' in dot


def test_unknown_node_type_raises():
    class NotARealNode:
        pass

    with pytest.raises(TypeError):
        ast_to_dot(NotARealNode()) 


def test_render_writes_image_file(tmp_path):
    dot_source = ast_to_dot(parse("a(b|c)*"))
    outfile = tmp_path / "ast.png"
    result_path = render(dot_source, str(outfile))
    assert result_path == str(outfile)
    assert outfile.exists()
    assert outfile.stat().st_size > 0
