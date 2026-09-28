"""Tests for fslib.cli: parse, tree, automaton, dfa, min, match commands."""

import sys

from fslib.cli import FslibCLI, main


def test_parse_returns_ast_repr():
    cli = FslibCLI()
    assert cli.parse("ab") == "Concat(left=Literal(char='a'), right=Literal(char='b'))"


def test_tree_prints_dot_to_stdout_when_no_out():
    cli = FslibCLI()
    dot = cli.tree("a")
    assert dot.startswith("digraph AST {")


def test_tree_writes_dot_file(tmp_path):
    cli = FslibCLI()
    out = tmp_path / "ast.dot"
    result = cli.tree("a", out=str(out))
    assert result == f"wrote {out}"
    assert out.read_text().startswith("digraph AST {")


def test_tree_renders_image(tmp_path):
    cli = FslibCLI()
    out = tmp_path / "ast.png"
    cli.tree("a(b|c)*", out=str(out))
    assert out.exists()
    assert out.stat().st_size > 0


def test_automaton_prints_dot_to_stdout():
    cli = FslibCLI()
    dot = cli.automaton("a")
    assert dot.startswith("digraph FSM {")


def test_automaton_writes_dot_file(tmp_path):
    cli = FslibCLI()
    out = tmp_path / "nfa.dot"
    cli.automaton("a", out=str(out))
    assert out.read_text().startswith("digraph FSM {")


def test_dfa_writes_dot_file(tmp_path):
    cli = FslibCLI()
    out = tmp_path / "dfa.dot"
    cli.dfa("a(b|c)*", out=str(out))
    assert out.read_text().startswith("digraph FSM {")


def test_min_writes_dot_file(tmp_path):
    cli = FslibCLI()
    out = tmp_path / "min.dot"
    cli.min("a(b|c)*", out=str(out))
    assert out.read_text().startswith("digraph FSM {")


def test_match_true_and_false():
    cli = FslibCLI()
    assert cli.match("a(b|c)*", "abcbc") is True
    assert cli.match("a(b|c)*", "abd") is False


def test_main_runs_via_fire(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["fslib", "parse", "a"])
    main()
    captured = capsys.readouterr()
    assert "Literal" in captured.out
