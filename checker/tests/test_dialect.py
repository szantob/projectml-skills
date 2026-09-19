"""Each point of the contract's YAML dialect, tested on its own, so that a
broken correction names itself rather than surfacing as a failed case."""

import pytest

import dialect


def test_on_yes_no_and_off_are_strings():
    assert dialect.load("a: on\nb: yes\nc: no\nd: off\n") == {
        "a": "on",
        "b": "yes",
        "c": "no",
        "d": "off",
    }


def test_only_true_and_false_are_booleans():
    assert dialect.load("a: true\nb: False\n") == {"a": True, "b": False}


def test_a_leading_zero_is_decimal():
    assert dialect.load("a: 010\nb: 0o10\nc: 0x1F\n") == {"a": 10, "b": 8, "c": 31}


def test_a_decimal_point_makes_a_float():
    assert dialect.load("a: 1.0\n") == {"a": 1.0}


def test_null_has_four_spellings_and_an_empty_value():
    assert dialect.load("a: null\nb: ~\nc: Null\nd:\n") == {
        "a": None,
        "b": None,
        "c": None,
        "d": None,
    }


def test_a_date_is_a_string():
    assert dialect.load("a: 2026-09-19\n") == {"a": "2026-09-19"}


def test_a_merge_key_is_an_ordinary_key():
    assert dialect.load("c:\n  <<: {x: 1}\n  y: 2\n") == {"c": {"<<": {"x": 1}, "y": 2}}


def test_an_anchor_never_aliased_is_read_as_if_absent():
    assert dialect.load("a: &x 1\nb: 2\n") == {"a": 1, "b": 2}


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("a: 1\na: 2\n", id="a repeated key"),
        pytest.param("a: 1\n---\nb: 2\n", id="two documents"),
        pytest.param("a: &x 1\nb: *x\n", id="an alias"),
        pytest.param("a: [unclosed\n", id="a syntax error"),
    ],
)
def test_the_unreadable_is_refused(text):
    with pytest.raises(dialect.Unreadable):
        dialect.load(text)
