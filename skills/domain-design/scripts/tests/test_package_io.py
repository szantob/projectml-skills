"""The canonical writer: what it writes is read back as what was written."""

from pathlib import Path

import pytest

import dialect
import package_io

CONFORMANCE = Path(__file__).resolve().parents[4] / "contract" / "conformance"


def _readable_cases_iter():
    for case in sorted(CONFORMANCE.iterdir()):
        text = (case / "package.yaml").read_text(encoding="utf-8")
        try:
            dialect.load(text)
        except dialect.Unreadable:
            continue
        yield pytest.param(text, id=case.name)


@pytest.mark.parametrize("text", list(_readable_cases_iter()))
def test_every_readable_case_reads_back_as_itself(text):
    document = dialect.load(text)
    assert dialect.load(package_io.dump(document)) == document


@pytest.mark.parametrize("text", list(_readable_cases_iter()))
def test_writing_is_idempotent(text):
    once = package_io.dump(dialect.load(text))
    assert package_io.dump(dialect.load(once)) == once


@pytest.mark.parametrize(
    "value",
    [
        "a\x85b",
        "a b",
        "a b",
        "first line\nsecond line\n",
        "trailing space \nnext",
        "null",
        "true",
        "on",
        "0o17",
        "0x1F",
        "010",
        "1e3",
        ".inf",
        "2026-09-24",
        "<<",
        "a: b",
        "{x}",
        "# not a comment",
        "",
        " leading space",
        "Ledfal szélesség – ő",
    ],
)
def test_a_string_stays_that_string(value):
    document = {"text": value, "list": [value]}
    assert dialect.load(package_io.dump(document)) == document


def test_the_three_line_breaks_are_written_quoted():
    # The contract says whatever writes a package quotes any text holding
    # one; the dialect refuses them unquoted, so reading back would already
    # fail - this pins that it is quoting, not luck, that avoids it.
    written = package_io.dump({"text": "a b"})
    assert '"' in written


def test_no_anchor_is_ever_written():
    shared = {"id": "x"}
    written = package_io.dump({"a": shared, "b": shared})
    assert "&" not in written and "*" not in written


def test_keys_keep_their_order():
    written = package_io.dump({"zeta": 1, "alpha": 2})
    assert written.index("zeta") < written.index("alpha")


def test_a_list_under_a_key_is_indented():
    written = package_io.dump({"kinds": [{"id": "a"}]})
    assert "kinds:\n  - id: a\n" in written


def test_multi_line_prose_is_a_literal_block():
    written = package_io.dump({"text": "one\ntwo\n"})
    assert "text: |" in written


def test_long_prose_is_not_folded():
    value = " ".join(["word"] * 60)
    written = package_io.dump({"text": value})
    assert value in written


def test_write_replaces_the_file_and_ends_in_one_line_feed(tmp_path):
    path = tmp_path / "package.yaml"
    path.write_text("old\n", encoding="utf-8")
    package_io.write(path, {"name": "é"})
    raw = path.read_bytes()
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert b"\r" not in raw
    assert dialect.load(raw.decode("utf-8")) == {"name": "é"}
    assert [p.name for p in tmp_path.iterdir()] == ["package.yaml"]
