import pytest

from fslib.regex.ast import (
    Concat,
    Epsilon,
    Literal,
    Plus,
    Star,
    Union,
    Wildcard,
)
from fslib.regex.errors import RegexSyntaxError
from fslib.regex.parser import parse


def test_empty_pattern_is_epsilon():
    assert parse("") == Epsilon()


def test_single_literal():
    assert parse("a") == Literal("a")


def test_concatenation():
    assert parse("ab") == Concat(Literal("a"), Literal("b"))


def test_union():
    assert parse("a|b") == Union(Literal("a"), Literal("b"))


def test_union_with_empty_side():
    assert parse("a|") == Union(Literal("a"), Epsilon())
    assert parse("|a") == Union(Epsilon(), Literal("a"))


def test_star_plus():
    assert parse("a*") == Star(Literal("a"))
    assert parse("a+") == Plus(Literal("a"))


def test_repeat_operators_chain():
    assert parse("a*+") == Plus(Star(Literal("a")))


def test_wildcard():
    assert parse(".") == Wildcard()
    assert parse("a.b") == Concat(Concat(Literal("a"), Wildcard()), Literal("b"))


def test_grouping_overrides_precedence():
    assert parse("(a|b)c") == Concat(Union(Literal("a"), Literal("b")), Literal("c"))


def test_empty_group_is_epsilon():
    assert parse("()") == Epsilon()


def test_star_binds_tighter_than_concat():
    assert parse("ab*") == Concat(Literal("a"), Star(Literal("b")))


def test_union_binds_looser_than_concat():
    assert parse("ab|c") == Union(Concat(Literal("a"), Literal("b")), Literal("c"))


def test_escaping_metacharacters():
    for meta in "|*+().\\":
        assert parse("\\" + meta) == Literal(meta)


def test_escaping_ordinary_character():
    assert parse("\\n") == Literal("n")


@pytest.mark.parametrize(
    "pattern",
    ["(a", "(a|b", "((a)"],
)
def test_unbalanced_open_paren_raises(pattern):
    with pytest.raises(RegexSyntaxError, match="unbalanced"):
        parse(pattern)


@pytest.mark.parametrize("pattern", [")", "a)", "(a))"])
def test_unmatched_close_paren_raises(pattern):
    with pytest.raises(RegexSyntaxError, match="unmatched"):
        parse(pattern)


@pytest.mark.parametrize("pattern", ["*a", "+a", "(*)"])
def test_nothing_to_repeat_raises(pattern):
    with pytest.raises(RegexSyntaxError, match="nothing to repeat"):
        parse(pattern)


def test_trailing_escape_raises():
    with pytest.raises(RegexSyntaxError, match="dangling escape"):
        parse("a\\")


def test_syntax_error_message_has_caret_at_position():
    with pytest.raises(RegexSyntaxError) as exc_info:
        parse("a)")
    err = exc_info.value
    assert err.position == 1
    lines = str(err).splitlines()
    assert lines[1] == "a)"
    assert lines[2] == " ^"


@pytest.mark.parametrize(
    "spaced, tight",
    [
        ("a b", "ab"),
        ("a | b", "a|b"),
        ("  a  |  b  ", "a|b"),
        ("( a | b ) c*", "(a|b)c*"),
        (".*a.*a | .*b.*b", ".*a.*a|.*b.*b"),
        ("\ta\nb ", "ab"),
    ],
)
def test_whitespace_is_not_significant(spaced, tight):
    assert parse(spaced) == parse(tight)


def test_whitespace_only_pattern_is_epsilon():
    assert parse("   ") == Epsilon()


def test_escaped_space_stays_a_literal():
    assert parse(r"a\ b") == Concat(Concat(Literal("a"), Literal(" ")), Literal("b"))
    assert parse(r"a\ ") == Concat(Literal("a"), Literal(" "))


def test_plus_is_kleene_plus_even_when_spaced():
    # '+' never means union, whatever the spacing: 'a + b' is a(+)b, not a|b
    assert parse("a + b") == Concat(Plus(Literal("a")), Literal("b"))
    assert parse("a + b") == parse("a+b")
    assert parse("a + b") != parse("a|b")


def test_literal_rejects_non_single_char():
    with pytest.raises(ValueError):
        Literal("ab")
