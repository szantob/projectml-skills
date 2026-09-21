"""Every case in the contract's corpus, run through the checker's functions.

Results are compared as the contract says: parse verdict, schema verdict, and
issues and gaps as multisets of codes and fields — never as wording, and never
in order.
"""

import json
from collections import Counter

import pytest

import contract_schema
import dialect
import findings

CASES = contract_schema.CONTRACT / "conformance"
NAMES = sorted(path.name for path in CASES.iterdir() if path.is_dir())


def _asserts_nothing_else(expected, *also):
    """A case the checker stops short on carries its verdict and nothing more.

    The contract refuses issues or gaps beside such a verdict rather than
    trusting them: nothing was computed for them to be compared against, so
    whatever they said would go unread.
    """
    for key in ("issues", "gaps", *also):
        assert key not in expected, f"a case stopped at its verdict carries no {key!r}"


def _case(name):
    folder = CASES / name
    return (
        (folder / "package.yaml").read_text(encoding="utf-8"),
        json.loads((folder / "expected.json").read_text(encoding="utf-8")),
    )


@pytest.mark.parametrize("name", NAMES)
def test_case(name):
    text, expected = _case(name)

    if expected.get("parses", True) is False:
        with pytest.raises(dialect.Unreadable):
            dialect.load(text)
        _asserts_nothing_else(expected, "schemaValid")
        return

    document = dialect.load(text)
    assert (contract_schema.misfits(document) == []) is expected["schemaValid"]
    if not expected["schemaValid"]:
        _asserts_nothing_else(expected)
        return

    assert Counter(
        (issue.code, issue.kind) for issue in findings.issues(document)
    ) == Counter((issue["code"], issue["kind"]) for issue in expected.get("issues", []))
    assert Counter(
        (gap.kind, gap.field, gap.parameter) for gap in findings.gaps(document)
    ) == Counter(
        (gap["kind"], gap["field"], gap["parameter"])
        for gap in expected.get("gaps", [])
    )


def test_the_corpus_is_all_there():
    assert len(NAMES) == 52


def test_every_issue_code_and_every_gap_field_has_a_case():
    """The contract's floor for the corpus, which it says a test enforces.

    It is stated in ``contract/README.md``, so the repository that holds the
    contract is the one that has to hold the test as well.
    """
    vocabulary = json.loads(
        (contract_schema.CONTRACT / "vocabulary.json").read_text(encoding="utf-8")
    )
    codes = set()
    fields = set()
    for name in NAMES:
        _text, expected = _case(name)
        codes.update(issue["code"] for issue in expected.get("issues", []))
        fields.update(gap["field"] for gap in expected.get("gaps", []))

    assert sorted(codes) == sorted(vocabulary["issueCodes"])
    assert sorted(fields) == sorted(vocabulary["gapFields"])
