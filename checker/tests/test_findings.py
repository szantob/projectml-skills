"""What the corpus cannot pin, because it compares as sets: the order gaps
come in, and the shape of what the functions return."""

import findings


COUNT = "00000000-0000-4000-9000-000000000001"


def _blank_kind(kind_id):
    return {
        "id": kind_id,
        "name": "",
        "abstract": False,
        "text": "",
        "whenItApplies": "",
        "parameters": [
            {"id": COUNT, "name": "", "valueDomainId": "headcount", "whatToAsk": ""}
        ],
        "rules": [
            {
                "id": "r1",
                "type": "ConflictRule",
                "inForce": True,
                "guard": [{"parameter": COUNT, "operation": "equals", "constant": ""}],
                "whenItApplies": "",
                "whatToLookFor": "",
                "implies": None,
            }
        ],
        "howItWouldBeVerified": "",
        "wordingRule": "",
        "specialises": None,
    }


def _blank_package():
    return {
        "schemaVersion": 5,
        "name": "Blank",
        "version": "",
        "valueDomains": [
            {
                "id": "headcount",
                "name": "Headcount",
                "comparability": "ordered",
                "description": "",
            }
        ],
        "kinds": [_blank_kind("second"), _blank_kind("first")],
    }


def test_gaps_follow_the_file():
    expected = []
    for kind_id in ("second", "first"):
        expected += [
            findings.Gap(kind_id, "name", None),
            findings.Gap(kind_id, "text", None),
            findings.Gap(kind_id, "whenItApplies", None),
            findings.Gap(kind_id, "parameterName", COUNT),
            findings.Gap(kind_id, "whatToAsk", COUNT),
            findings.Gap(kind_id, "guardConstant", COUNT),
            findings.Gap(kind_id, "ruleWhenItApplies", None),
            findings.Gap(kind_id, "ruleWhatToLookFor", None),
            findings.Gap(kind_id, "howItWouldBeVerified", None),
            findings.Gap(kind_id, "wordingRule", None),
        ]
    assert findings.gaps(_blank_package()) == expected


def test_an_abstract_kind_leaves_out_the_three_that_do_not_apply():
    package = _blank_package()
    package["kinds"] = [dict(_blank_kind("only"), abstract=True)]
    fields = [gap.field for gap in findings.gaps(package)]
    assert "text" not in fields
    assert "howItWouldBeVerified" not in fields
    assert "wordingRule" not in fields
    assert "whatToAsk" in fields


def test_each_level_of_comparability_includes_the_one_below():
    allowed = findings.ALLOWED_OPERATIONS
    assert allowed["notComparable"] == set()
    assert allowed["notComparable"] < allowed["equality"] < allowed["ordered"]
    assert len(allowed["ordered"]) == 6


def test_an_issue_carries_a_message():
    package = {
        "schemaVersion": 5,
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
