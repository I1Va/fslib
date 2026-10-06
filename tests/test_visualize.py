import pytest

from fslib.fsm import FSM
from fslib.passes.construct import thompson
from fslib.regex.ast import Concat, Literal, Star, Union
from fslib.regex.parser import parse
from fslib.viz import ast_to_dot, fsm_to_dot, render


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


def _ends_in_a() -> FSM:
    return FSM(
        states={0, 1},
        alphabet={"a", "b"},
        transitions={0: {"a": {1}, "b": {0}}, 1: {"a": {1}, "b": {0}}},
        start=0,
        accepting={1},
    )


def test_fsm_to_dot_marks_start_and_accepting_states():
    dot = fsm_to_dot(_ends_in_a())
    assert dot.startswith("digraph FSM {")
    assert dot.endswith("}")
    assert "__start -> s0;" in dot
    assert 's0 [shape=circle, label="0"];' in dot
    assert 's1 [shape=doublecircle, label="1"];' in dot


def test_fsm_to_dot_has_one_edge_per_state_pair():
    dot = fsm_to_dot(_ends_in_a())
    assert 's0 -> s1 [label="a"];' in dot
    assert 's0 -> s0 [label="b"];' in dot
    assert 's1 -> s1 [label="a"];' in dot
    assert 's1 -> s0 [label="b"];' in dot


def test_fsm_to_dot_merges_parallel_edges():
    fsm = FSM(
        states={0, 1},
        alphabet={"a", "b", "c"},
        transitions={0: {"a": {1}, "b": {1}, "c": {1}}},
        start=0,
        accepting={1},
    )
    dot = fsm_to_dot(fsm)
    assert dot.count("s0 -> s1") == 1
    assert 's0 -> s1 [label="a,b,c"];' in dot


def test_fsm_to_dot_shows_epsilon_edges():
    fsm = FSM(
        states={0, 1},
        alphabet=set(),
        transitions={0: {None: {1}}},
        start=0,
        accepting={1},
    )
    dot = fsm_to_dot(fsm)
    assert '"ε"' in dot


def test_fsm_to_dot_quotes_symbols_that_clash_with_the_separator():
    fsm = FSM(
        states={0, 1},
        alphabet={",", " ", "a"},
        transitions={0: {",": {1}, " ": {1}, "a": {1}}},
        start=0,
        accepting={1},
    )
    dot = fsm_to_dot(fsm)
    assert "','" in dot
    assert "' '" in dot
    assert ",,a" not in dot


def test_fsm_to_dot_render_writes_image_file(tmp_path):
    dot_source = fsm_to_dot(thompson(parse("a(b|c)*")))
    outfile = tmp_path / "fsm.png"
    result_path = render(dot_source, str(outfile))
    assert result_path == str(outfile)
    assert outfile.exists()
    assert outfile.stat().st_size > 0
