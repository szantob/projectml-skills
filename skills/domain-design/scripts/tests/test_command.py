"""What the command prints, and the exit status that says what kind of
answer it is."""

import io
from pathlib import Path

import contract_schema
import dialect
import diagram

CONFORMANCE = Path(__file__).resolve().parents[4] / "contract" / "conformance"

# The fixtures' identities. The corpus numbers its own the same way, from 1
# in each case.
PARENT = "00000000-0000-4000-8000-000000000001"
CHILD = "00000000-0000-4000-8000-000000000002"
S = "00000000-0000-4000-8000-000000000003"
T = "00000000-0000-4000-8000-000000000004"
GHOST = "00000000-0000-4000-8000-000000000099"
FIRST = "00000000-0000-4000-8000-000000000001"
SECOND = "00000000-0000-4000-8000-000000000002"
THIRD = "00000000-0000-4000-8000-000000000003"

CLEAN = """schemaVersion: 4
name: "Two kinds"
version: ""
valueDomains: []
kinds:
  - id: 00000000-0000-4000-8000-000000000001
    name: "Parent"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
  - id: 00000000-0000-4000-8000-000000000002
    name: "Child"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: 00000000-0000-4000-8000-000000000001
"""

TWINS = """schemaVersion: 4
name: "Two kinds carrying one identity"
version: ""
valueDomains: []
kinds:
  - id: 00000000-0000-4000-8000-000000000001
    name: "First"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
  - id: 00000000-0000-4000-8000-000000000001
    name: "Second"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
"""

CYCLIC = """schemaVersion: 4
name: "Two kinds specialising each other"
version: ""
valueDomains: []
kinds:
  - id: 00000000-0000-4000-8000-000000000001
    name: "Parent"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: 00000000-0000-4000-8000-000000000002
  - id: 00000000-0000-4000-8000-000000000002
    name: "Child"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: 00000000-0000-4000-8000-000000000001
"""


TWO_CHILDREN_ONE_IDENTITY = """schemaVersion: 4
name: "Two children sharing one identity"
version: ""
valueDomains: []
kinds:
  - id: 00000000-0000-4000-8000-000000000003
    name: "S"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
  - id: 00000000-0000-4000-8000-000000000004
    name: "T first"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: 00000000-0000-4000-8000-000000000003
  - id: 00000000-0000-4000-8000-000000000004
    name: "T second"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: 00000000-0000-4000-8000-000000000003
"""


def run(text, subject=None):
    out = io.StringIO()
    status = diagram.draw(text, subject, out)
    return status, out.getvalue()


def test_a_drawable_subject_exits_zero_and_writes_a_diagram():
    status, text = run(CLEAN, subject=CHILD)
    assert status == 0
    assert text.startswith("classDiagram")
    assert f"{diagram._sanitise(PARENT)} <|-- {diagram._sanitise(CHILD)}" in text


def test_two_kinds_sharing_a_child_identity_both_draw_and_it_says_so():
    # "t" (First) and "t" (Second) both specialise "s" and are both true
    # children of it — draw only what is true — but the package gives no
    # way to tell the two boxes apart, so the diagram must say that itself
    # rather than silently drawing two boxes and inventing a name for one.
    status, out = run(TWO_CHILDREN_ONE_IDENTITY, subject=S)
    assert status == 0
    assert out.startswith("classDiagram")
    assert f'class {diagram._sanitise(T)}["T first"]' in out
    assert f'class {diagram._sanitise(T)}_1["T second"]' in out
    assert f"%% The identity '{T}' is carried by 2 of the drawn kinds" in out
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
    status, text = run(CLEAN, subject=GHOST)
    assert status == 1
    assert "No kind carries" in text


def test_an_identity_two_kinds_carry_names_both_positions():
    status, text = run(TWINS, subject=PARENT)
    assert status == 1
    assert "2 kinds" in text
    assert "[0, 1]" in text
    assert "duplicate-kind-id" in text


def test_a_subject_on_a_cycle_says_so_rather_than_drawing():
    status, text = run(CYCLIC, subject=CHILD)
    assert status == 1
    assert "cycle" in text
    assert "specialisation-cycle" in text


def test_ambiguity_from_a_cyclic_carrier_is_not_hidden_by_filtering():
    # The four-kind reproduction from the review: "p" and "q" specialise
    # each other, a cycle, and a second, non-cyclic kind also carries "p".
    # Counting only off-cycle carriers would call "p" unambiguous and
    # silently pick one of the two kinds named "p"; drawing "s" must refuse
    # instead, the way the checker's own duplicate-kind-id does.
    text = """schemaVersion: 4
name: "A cyclic pair plus a root sharing its identity"
version: ""
valueDomains: []
kinds:
  - id: 00000000-0000-4000-8000-000000000005
    name: "P0"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: 00000000-0000-4000-8000-000000000006
  - id: 00000000-0000-4000-8000-000000000006
    name: "Q"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: 00000000-0000-4000-8000-000000000005
  - id: 00000000-0000-4000-8000-000000000005
    name: "P2"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: null
  - id: 00000000-0000-4000-8000-000000000003
    name: "S"
    text: "shall hold"
    whenItApplies: "Always."
    parameters: []
    rules: []
    howItWouldBeVerified: "By inspection."
    wordingRule: "One sentence."
    specialises: 00000000-0000-4000-8000-000000000005
"""
    status, out = run(text, subject=S)
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
    status, out = run(text, subject=THIRD)
    assert status == 0
    assert out.startswith("classDiagram")
    assert "RequirementDefinition" not in out
    assert f"%% The parent it names, '{FIRST}'" in out
    assert "specialisation-cycle" in out


def test_an_unknown_parent_gets_the_same_symmetric_sentence():
    # Corpus case 06: "a" specialises "ghost", which no kind carries at
    # all. This used to draw a lone, unexplained box; it must now say why,
    # the same way case 33 already does for a cyclic parent — a "%%" line
    # citing unknown-parent instead of specialisation-cycle.
    path = CONFORMANCE / "06-unknown-parent" / "package.yaml"
    text = path.read_text(encoding="utf-8")
    status, out = run(text, subject=FIRST)
    assert status == 0
    assert out.startswith("classDiagram")
    assert "RequirementDefinition" not in out
    assert f"%% The parent it names, '{SECOND}'" in out
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
    _, cyclic_out = run(cyclic_text, subject=THIRD)
    _, unknown_out = run(unknown_text, subject=FIRST)
    assert cyclic_out != unknown_out
    assert "specialisation-cycle" in cyclic_out
    assert "specialisation-cycle" not in unknown_out
    assert "unknown-parent" in unknown_out


def _grammatical_lines(out):
    """Every line of ``out`` that belongs to a Mermaid class diagram: the
    header, a tab-indented statement, or a trailing ``%%`` comment. A line
    that is none of these falls outside the fence's grammar wherever it is
    pasted."""
    def _in_grammar(line):
        return line == "classDiagram" or line.startswith("\t") or line.startswith("%%")

    return [line for line in out.splitlines() if not _in_grammar(line)]


def test_a_name_of_one_next_line_character_stays_inside_the_grammar():
    # Corpus case 50: the kind's name is a single U+0085 (NEXT LINE)
    # character. `str.splitlines()` reads that as ending a line, the same
    # as `\n` or `\r`, but the flattening step used to only know
    # `WHITESPACE` - the contract's narrower notion of blank text, which
    # deliberately leaves U+0085 out - so the character reached the label
    # unescaped and split the diagram's own fence in two. This does not
    # assert the label's exact text, only that nothing broke out of the
    # grammar the fence depends on.
    path = CONFORMANCE / "50-a-name-of-one-next-line-character" / "package.yaml"
    text = path.read_text(encoding="utf-8")
    status, out = run(text, subject=FIRST)
    assert status == 0
    assert _grammatical_lines(out) == []


def test_every_drawable_kind_in_the_corpus_stays_inside_the_grammar():
    # The sweep behind the case above: every kind, in every conformance
    # package, tried once per distinct identity (a second kind sharing one
    # only ever gets the same duplicate-kind-id refusal as the first) and
    # drawn where drawing succeeds. Case 50 was the one counterexample this
    # found among the corpus's successful draws; the property must now hold
    # for all of them, not just that one.
    checked = 0
    for path in sorted(CONFORMANCE.glob("*/package.yaml")):
        text = path.read_text(encoding="utf-8")
        try:
            document = dialect.load(text)
        except dialect.Unreadable:
            continue
        if contract_schema.misfits(document):
            continue
        seen = set()
        for kind in document["kinds"]:
            identity = kind["id"]
            if identity in seen:
                continue
            seen.add(identity)
            status, out = run(text, subject=identity)
            if status != 0:
                continue
            checked += 1
            assert _grammatical_lines(out) == [], (path.parent.name, identity)
    # A floor, not the exact count: the corpus is free to grow without this
    # test needing to change, as long as it keeps drawing something.
    assert checked >= 30


def test_the_wrong_arguments_exit_two(capsys):
    assert diagram.main(["diagram.py"]) == 2
    assert "Usage:" in capsys.readouterr().out
