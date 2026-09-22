"""What the command prints, and the exit status that says what kind of
answer it is."""

import io

import diagram

CLEAN = """schemaVersion: 3
name: "Two kinds"
version: ""
valueDomains: []
kinds:
  - id: parent
    name: "Parent"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
  - id: child
    name: "Child"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: parent
"""

TWINS = """schemaVersion: 3
name: "Two kinds carrying one identity"
version: ""
valueDomains: []
kinds:
  - id: parent
    name: "First"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
  - id: parent
    name: "Second"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
"""

CYCLIC = """schemaVersion: 3
name: "Two kinds specialising each other"
version: ""
valueDomains: []
kinds:
  - id: parent
    name: "Parent"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: child
  - id: child
    name: "Child"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: parent
"""


def run(text, subject=None, position=None):
    out = io.StringIO()
    status = diagram.draw(text, subject, out, position=position)
    return status, out.getvalue()


def test_a_drawable_subject_exits_zero_and_writes_a_diagram():
    status, text = run(CLEAN, subject="child")
    assert status == 0
    assert text.startswith("classDiagram")
    assert "parent <|-- child" in text


def test_a_file_that_cannot_be_read_exits_two():
    status, text = run("kinds: [unclosed", subject="a")
    assert status == 2
    assert text.startswith("Cannot be read:")


def test_a_package_that_does_not_fit_the_schema_exits_two():
    status, text = run('schemaVersion: 3\nname: "x"\n', subject="a")
    assert status == 2
    assert text.startswith("Does not fit the schema:")


def test_an_identity_no_kind_carries_exits_one():
    status, text = run(CLEAN, subject="ghost")
    assert status == 1
    assert "no kind carries" in text


def test_an_identity_two_kinds_carry_names_both_positions():
    status, text = run(TWINS, subject="parent")
    assert status == 1
    assert "2 kinds" in text
    assert "[0, 1]" in text


def test_a_position_names_one_of_them_unambiguously():
    status, text = run(TWINS, position=1)
    assert status == 0
    assert text.startswith("classDiagram")


def test_a_subject_on_a_cycle_says_so_rather_than_drawing():
    status, text = run(CYCLIC, subject="child")
    assert status == 1
    assert "cycle" in text


def test_a_position_outside_the_package_exits_one():
    status, text = run(CLEAN, position=7)
    assert status == 1
    assert "2 kinds" in text


def test_the_wrong_arguments_exit_two(capsys):
    assert diagram.main(["diagram.py"]) == 2
    assert "Usage:" in capsys.readouterr().out
