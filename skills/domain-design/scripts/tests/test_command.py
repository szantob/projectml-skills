"""What the command prints, and the exit status that says what kind of
answer it is."""

import io
from pathlib import Path

import diagram

CONFORMANCE = Path(__file__).resolve().parents[4] / "contract" / "conformance"

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


TWO_CHILDREN_ONE_IDENTITY = """schemaVersion: 3
name: "Two children sharing one identity"
version: ""
valueDomains: []
kinds:
  - id: s
    name: "S"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
  - id: t
    name: "T first"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: s
  - id: t
    name: "T second"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: s
"""


def run(text, subject=None):
    out = io.StringIO()
    status = diagram.draw(text, subject, out)
    return status, out.getvalue()


def test_a_drawable_subject_exits_zero_and_writes_a_diagram():
    status, text = run(CLEAN, subject="child")
    assert status == 0
    assert text.startswith("classDiagram")
    assert "parent <|-- child" in text


def test_two_kinds_sharing_a_child_identity_both_draw_and_it_says_so():
    # "t" (First) and "t" (Second) both specialise "s" and are both true
    # children of it — draw only what is true — but the package gives no
    # way to tell the two boxes apart, so the diagram must say that itself
    # rather than silently drawing two boxes and inventing a name for one.
    status, out = run(TWO_CHILDREN_ONE_IDENTITY, subject="s")
    assert status == 0
    assert out.startswith("classDiagram")
    assert 'class t["T first"]' in out
    assert 'class t_1["T second"]' in out
    assert "%% The identity 't' is carried by 2 of the drawn kinds" in out
    assert "duplicate-kind-id" in out


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
    assert "No kind carries" in text


def test_an_identity_two_kinds_carry_names_both_positions():
    status, text = run(TWINS, subject="parent")
    assert status == 1
    assert "2 kinds" in text
    assert "[0, 1]" in text
    assert "duplicate-kind-id" in text


def test_a_subject_on_a_cycle_says_so_rather_than_drawing():
    status, text = run(CYCLIC, subject="child")
    assert status == 1
    assert "cycle" in text
    assert "specialisation-cycle" in text


def test_ambiguity_from_a_cyclic_carrier_is_not_hidden_by_filtering():
    # The four-kind reproduction from the review: "p" and "q" specialise
    # each other, a cycle, and a second, non-cyclic kind also carries "p".
    # Counting only off-cycle carriers would call "p" unambiguous and
    # silently pick one of the two kinds named "p"; drawing "s" must refuse
    # instead, the way the checker's own duplicate-kind-id does.
    text = """schemaVersion: 3
name: "A cyclic pair plus a root sharing its identity"
version: ""
valueDomains: []
kinds:
  - id: p
    name: "P0"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: q
  - id: q
    name: "Q"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: p
  - id: p
    name: "P2"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
  - id: s
    name: "S"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: p
"""
    status, out = run(text, subject="s")
    assert status == 1
    assert "2 kinds" in out
    assert "[0, 2]" in out


def test_a_kind_below_a_cycle_draws_and_says_why_its_parent_is_absent():
    # Corpus case 33: "c" descends from "a", which sits on a cycle with "b".
    # Drawing "c" must not be a lone box with nothing said — the parent is
    # carried, just not drawn, and that has to be in words, as a Mermaid
    # comment so the fence around the diagram stays valid.
    path = CONFORMANCE / "33-a-kind-descending-from-a-cycle" / "package.yaml"
    text = path.read_text(encoding="utf-8")
    status, out = run(text, subject="c")
    assert status == 0
    assert out.startswith("classDiagram")
    assert "RequirementDefinition" not in out
    assert "%% The parent it names, 'a'" in out
    assert "specialisation-cycle" in out


def test_an_unknown_parent_gets_the_same_symmetric_sentence():
    # Corpus case 06: "a" specialises "ghost", which no kind carries at
    # all. This used to draw a lone, unexplained box; it must now say why,
    # the same way case 33 already does for a cyclic parent — a "%%" line
    # citing unknown-parent instead of specialisation-cycle.
    path = CONFORMANCE / "06-unknown-parent" / "package.yaml"
    text = path.read_text(encoding="utf-8")
    status, out = run(text, subject="a")
    assert status == 0
    assert out.startswith("classDiagram")
    assert "RequirementDefinition" not in out
    assert "%% The parent it names, 'ghost'" in out
    assert "unknown-parent" in out


def test_a_cyclic_parent_and_an_unknown_parent_are_told_apart():
    # Case 33 (a parent that exists but sits on a cycle) and case 06 (a
    # parent no kind carries) must no longer render the same unexplained,
    # single-box diagram.
    cyclic_text = (
        CONFORMANCE / "33-a-kind-descending-from-a-cycle" / "package.yaml"
    ).read_text(encoding="utf-8")
    unknown_text = (CONFORMANCE / "06-unknown-parent" / "package.yaml").read_text(
        encoding="utf-8"
    )
    _, cyclic_out = run(cyclic_text, subject="c")
    _, unknown_out = run(unknown_text, subject="a")
    assert cyclic_out != unknown_out
    assert "specialisation-cycle" in cyclic_out
    assert "specialisation-cycle" not in unknown_out
    assert "unknown-parent" in unknown_out


def test_the_wrong_arguments_exit_two(capsys):
    assert diagram.main(["diagram.py"]) == 2
    assert "Usage:" in capsys.readouterr().out
