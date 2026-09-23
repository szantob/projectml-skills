"""What the emitter draws, and what it refuses to claim."""

import diagram
import tree
from tree import Neighbourhood


def kind(identity, specialises=None, name=""):
    return {
        "id": identity,
        "name": name,
        "text": "",
        "whenItApplies": "",
        "parameters": [],
        "rules": [],
        "howItWouldBeVerified": "",
        "wordingRule": "",
        "specialises": specialises,
    }


def draw(kinds, subject):
    return diagram.to_mermaid(kinds, tree.neighbourhood(kinds, subject))


def test_it_is_a_class_diagram():
    assert draw([kind("a")], 0).startswith("classDiagram")


def test_a_root_kind_hangs_off_the_abstract_root():
    drawn = draw([kind("a")], 0)
    assert "class RequirementDefinition {" in drawn
    assert "<<abstract>>" in drawn
    assert "RequirementDefinition <|-- a" in drawn


def test_a_child_hangs_off_its_parent():
    drawn = draw([kind("a"), kind("b", "a")], 1)
    assert "a <|-- b" in drawn


def test_the_parent_gets_no_edge_above_it():
    # The parent's own parent is not drawn, so an edge up to the abstract
    # root would call the parent a root kind when it is not.
    kinds = [kind("grandparent"), kind("parent", "grandparent"), kind("a", "parent")]
    drawn = draw(kinds, 2)
    assert "parent <|-- a" in drawn
    assert "RequirementDefinition" not in drawn


def test_a_subject_naming_a_parent_that_does_not_exist_is_no_root():
    drawn = draw([kind("a", "ghost")], 0)
    assert "RequirementDefinition" not in drawn
    assert "<|--" not in drawn


def test_a_subject_naming_a_parent_on_a_cycle_gets_no_edge_either():
    # "a" and "b" specialise each other, a cycle; "c" descends from "a" but
    # is not on the cycle. The parent is carried, but a kind on a cycle has
    # no place in a tree, so this must draw exactly like a missing parent:
    # no edge up, no false claim that "c" is a root kind, and no box for
    # the cyclic parent either — a floating box drawn nowhere would be
    # silent about what it is doing there.
    kinds = [kind("a", "b", name="Ay"), kind("b", "a"), kind("c", "a")]
    drawn = draw(kinds, 2)
    assert "RequirementDefinition" not in drawn
    assert "<|--" not in drawn
    assert "Ay" not in drawn


def test_root_edge_is_a_positive_test_not_a_fallthrough():
    # A hand-built Neighbourhood with every parent flag clear, over a kind
    # that still names a parent, must not draw the root edge. Whether that
    # edge is true is decided from the package's own `specialises`, not
    # from near having nothing else to say about the parent — a fourth
    # parent state, if one ever arrives, must fall into "no edge" too.
    kinds = [kind("a", "ghost")]
    near = Neighbourhood(
        subject=0, parent=None, parent_missing=False, parent_cyclic=None,
        children=(),
    )
    drawn = diagram.to_mermaid(kinds, near)
    assert "RequirementDefinition" not in drawn
    assert "<|--" not in drawn


def test_two_children_sharing_an_identity_both_draw_and_the_diagram_says_so():
    # "s" is the subject; two children both carry the identity "t" and both
    # specialise "s". Both edges are true — draw only what is true — but a
    # shared identity is not a reference that has to resolve to one kind
    # here, it is two kinds pointing at the subject, so both are drawn. The
    # package gives no way to tell their boxes apart, so the diagram must.
    kinds = [
        kind("s"),
        kind("t", "s", name="T first"),
        kind("t", "s", name="T second"),
    ]
    drawn = draw(kinds, 0)
    lines = drawn.splitlines()
    assert "\ts <|-- t" in lines
    assert "\ts <|-- t_1" in lines
    assert 'class t["T first"]' in drawn
    assert 'class t_1["T second"]' in drawn
    assert "%% The identity 't' is carried by 2 of the drawn kinds" in drawn
    assert "duplicate-kind-id" in drawn


def test_a_missing_parent_says_why_in_a_mermaid_comment():
    drawn = draw([kind("a", "ghost")], 0)
    assert "%% The parent it names, 'ghost'" in drawn
    assert "unknown-parent" in drawn


def test_a_cyclic_parent_says_why_in_a_mermaid_comment():
    kinds = [kind("a", "b"), kind("b", "a"), kind("c", "a")]
    drawn = draw(kinds, 2)
    assert "%% The parent it names, 'a'" in drawn
    assert "specialisation-cycle" in drawn


def test_children_are_drawn_below_the_subject():
    kinds = [kind("a"), kind("b", "a"), kind("c", "a")]
    drawn = draw(kinds, 0)
    assert "a <|-- b" in drawn
    assert "a <|-- c" in drawn


def test_a_named_kind_carries_its_name():
    assert 'class a["Capacity"]' in draw([kind("a", name="Capacity")], 0)


def test_an_unnamed_kind_shows_its_identifier_alone():
    assert "class a[" not in draw([kind("a")], 0)


def test_a_name_is_flattened_and_its_quotes_made_safe():
    drawn = draw([kind("a", name='the "loud"\n one')], 0)
    assert 'class a["the #quot;loud#quot; one"]' in drawn


def test_an_identifier_mermaid_cannot_take_is_made_safe():
    drawn = draw([kind("a b-c")], 0)
    assert "RequirementDefinition <|-- a_b_c" in drawn


def test_an_identifier_starting_with_a_digit_gains_a_prefix():
    assert "<|-- _1st" in draw([kind("1st")], 0)


def test_an_empty_identifier_still_gets_a_name():
    assert "<|-- _" in draw([kind("")], 0)


def test_two_drawn_kinds_sanitising_alike_stay_distinct():
    kinds = [kind("a"), kind("a-b", "a"), kind("a_b", "a")]
    drawn = draw(kinds, 0)
    assert "a <|-- a_b" in drawn
    assert "a <|-- a_b_1" in drawn


def test_a_kind_called_like_the_root_does_not_take_its_name():
    drawn = draw([kind("RequirementDefinition")], 0)
    assert "RequirementDefinition <|-- RequirementDefinition_1" in drawn


def test_the_subject_is_marked():
    drawn = draw([kind("a"), kind("b", "a")], 1)
    assert "style b fill:#fff3bf,stroke:#a06800,stroke-width:3px" in drawn
