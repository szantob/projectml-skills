"""What the emitter draws, and what it refuses to claim."""

import diagram
import tree


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
