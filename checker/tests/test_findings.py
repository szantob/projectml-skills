"""What the corpus cannot pin, because it compares as sets: the order gaps
come in, and the shape of what the functions return."""

import findings


def _blank_kind(kind_id):
    return {
        "id": kind_id,
        "name": "",
        "text": "",
        "whenItApplies": "",
        "parameters": [{"name": "count", "valueDomainId": "headcount", "whatToAsk": ""}],
        "rules": [
            {
                "id": "r1",
                "type": "ConflictRule",
                "inForce": True,
                "whenItApplies": "",
                "whatToLookFor": "",
                "implies": None,
            }
        ],
        "howItWouldBeVerified": "",
        "wordingRule": "",
        "specialises": None,
    }


def test_gaps_follow_the_file():
    package = {
        "schemaVersion": 3,
        "name": "Blank",
        "version": "",
        "valueDomains": [{"id": "headcount", "name": "Headcount", "description": ""}],
        "kinds": [_blank_kind("second"), _blank_kind("first")],
    }
    expected = []
    for kind_id in ("second", "first"):
        expected += [
            findings.Gap(kind_id, "name", None),
            findings.Gap(kind_id, "text", None),
            findings.Gap(kind_id, "whenItApplies", None),
            findings.Gap(kind_id, "whatToAsk", "count"),
            findings.Gap(kind_id, "ruleWhenItApplies", None),
            findings.Gap(kind_id, "ruleWhatToLookFor", None),
            findings.Gap(kind_id, "howItWouldBeVerified", None),
            findings.Gap(kind_id, "wordingRule", None),
        ]
    assert findings.gaps(package) == expected


def test_an_issue_carries_a_message():
    package = {
        "schemaVersion": 3,
        "name": "Orphan",
        "version": "",
        "valueDomains": [],
        "kinds": [dict(_blank_kind("a"), specialises="ghost", parameters=[], rules=[])],
    }
    [issue] = findings.issues(package)
    assert issue.code == "unknown-parent"
    assert issue.kind == "a"
    assert issue.message.strip() != ""
