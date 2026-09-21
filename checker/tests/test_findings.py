"""What the corpus cannot pin, because it compares as sets: the order gaps
come in, and the shape of what the functions return."""

import findings


def _blank_kind(kind_id):
    return {
        "id": kind_id,
        "name": "",
        "text": "",
        "whenItApplies": "",
        "parameters": [
            {"name": "count", "valueDomainId": "headcount", "whatToAsk": ""}
        ],
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


def test_the_four_whitespace_characters_count_as_unwritten():
    for text in ("", " ", "\t", "\r", "\n", " \t\r\n "):
        assert findings._blank(text), repr(text)


def test_every_other_character_is_text_however_it_prints():
    # ``str.strip`` with no argument follows Unicode and would call all three
    # of these whitespace; the other implementation's ``trim`` calls two of
    # them whitespace. The contract names its own four so that neither
    # language decides.
    for text in ("\u00a0", "\ufeff", "\u0085"):
        assert not findings._blank(text), repr(text)


def test_a_placeholder_is_trimmed_of_the_four_and_nothing_else():
    assert findings._placeholders("seat {\tcount\n} people") == ["count"]
    assert findings._placeholders("seat {\u00a0count\u00a0} people") == [
        "\u00a0count\u00a0"
    ]
