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
        return

    document = dialect.load(text)
    assert (contract_schema.misfits(document) == []) is expected["schemaValid"]
    if not expected["schemaValid"]:
        return

    assert Counter((issue.code, issue.kind) for issue in findings.issues(document)) == Counter(
        (issue["code"], issue["kind"]) for issue in expected.get("issues", [])
    )
    assert Counter(
        (gap.kind, gap.field, gap.parameter) for gap in findings.gaps(document)
    ) == Counter(
        (gap["kind"], gap["field"], gap["parameter"]) for gap in expected.get("gaps", [])
    )


def test_the_corpus_is_all_there():
    assert len(NAMES) == 34
