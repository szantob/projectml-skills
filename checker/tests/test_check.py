"""The command: what it prints, and the exit status that says what kind of
answer it is."""

import io

import check
import contract_schema

CASES = contract_schema.CONTRACT / "conformance"


def _run(name):
    out = io.StringIO()
    status = check.check((CASES / name / "package.yaml").read_text(encoding="utf-8"), out)
    return status, out.getvalue()


def test_a_clean_package_exits_zero():
    status, text = _run("01-clean")
    assert status == 0
    assert "Fits the schema." in text
    assert "No issues." in text
    assert "No gaps." in text


def test_gaps_alone_still_exit_zero():
    status, text = _run("12-gaps-on-a-kind")
    assert status == 0
    assert "Gaps (5):" in text


def test_an_issue_exits_one():
    status, text = _run("02-duplicate-kind-id")
    assert status == 1
    assert "Issues (1):" in text
    assert "duplicate-kind-id" in text


def test_a_misfit_exits_one():
    status, text = _run("14-refuses-an-unknown-attribute")
    assert status == 1
    assert text.startswith("Does not fit the schema:")


def test_an_unreadable_file_exits_two():
    status, text = _run("19-unreadable-a-repeated-key")
    assert status == 2
    assert text.startswith("Cannot be read:")


def test_a_missing_file_exits_two(tmp_path, capsys):
    assert check.main(["check.py", str(tmp_path / "absent.yaml")]) == 2
    assert capsys.readouterr().out.startswith("Cannot be read:")


def test_the_wrong_number_of_arguments_exits_two(capsys):
    assert check.main(["check.py"]) == 2
    assert "Usage:" in capsys.readouterr().out
