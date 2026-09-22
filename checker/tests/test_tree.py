"""The specialisation tree, asked the questions a drawing asks of it."""

import pytest

import tree


def kind(identity, specialises=None):
    return {
        "id": identity,
        "name": "",
        "text": "",
        "whenItApplies": "",
        "parameters": [],
        "rules": [],
        "howItWouldBeVerified": "",
        "wordingRule": "",
        "specialises": specialises,
    }


def test_no_kind_carries_an_identity_nothing_declares():
    assert tree.positions_carrying([kind("a")], "b") == []


def test_one_kind_carries_it():
    assert tree.positions_carrying([kind("a"), kind("b")], "b") == [1]


def test_two_kinds_carrying_one_identity_give_both_positions_in_order():
    kinds = [kind("twin"), kind("other"), kind("twin")]
    assert tree.positions_carrying(kinds, "twin") == [0, 2]


def test_the_empty_identity_is_an_identity_like_any_other():
    assert tree.positions_carrying([kind(""), kind("a")], "") == [0]


def test_a_well_formed_tree_has_no_cyclic_positions():
    assert tree.cyclic_positions([kind("a"), kind("b", "a")]) == set()


def test_a_kind_specialising_itself_is_a_cycle_of_one():
    assert tree.cyclic_positions([kind("a", "a")]) == {0}


def test_both_members_of_a_two_kind_cycle_are_on_it():
    assert tree.cyclic_positions([kind("a", "b"), kind("b", "a")]) == {0, 1}


def test_a_kind_that_only_descends_from_a_cycle_is_not_on_it():
    kinds = [kind("a", "b"), kind("b", "a"), kind("c", "a")]
    assert tree.cyclic_positions(kinds) == {0, 1}


def test_two_kinds_sharing_a_cyclic_identity_are_both_on_the_cycle():
    kinds = [kind("twin", "twin"), kind("twin", "twin")]
    assert tree.cyclic_positions(kinds) == {0, 1}


def test_a_root_kind_has_no_parent_and_is_not_missing_one():
    near = tree.neighbourhood([kind("a")], 0)
    assert near.subject == 0
    assert near.parent is None
    assert near.parent_missing is False
    assert near.children == ()


def test_a_child_names_its_parent_s_position():
    near = tree.neighbourhood([kind("a"), kind("b", "a")], 1)
    assert near.parent == 0
    assert near.parent_missing is False


def test_children_come_in_declaration_order():
    kinds = [kind("a"), kind("b", "a"), kind("c"), kind("d", "a")]
    assert tree.neighbourhood(kinds, 0).children == (1, 3)


def test_only_direct_children_are_near():
    kinds = [kind("a"), kind("b", "a"), kind("c", "b")]
    assert tree.neighbourhood(kinds, 0).children == (1,)


def test_a_parent_no_kind_carries_is_missing_rather_than_refused():
    near = tree.neighbourhood([kind("a", "ghost")], 0)
    assert near.parent is None
    assert near.parent_missing is True


def test_a_subject_on_a_cycle_is_refused():
    with pytest.raises(tree.NotDrawable, match="cycle"):
        tree.neighbourhood([kind("a", "a")], 0)


def test_an_ambiguous_parent_is_refused_rather_than_chosen():
    kinds = [kind("twin"), kind("twin"), kind("child", "twin")]
    with pytest.raises(tree.NotDrawable, match="twin"):
        tree.neighbourhood(kinds, 2)


def test_an_ambiguous_subject_identity_is_refused():
    kinds = [kind("twin"), kind("twin")]
    with pytest.raises(tree.NotDrawable, match="twin"):
        tree.neighbourhood(kinds, 0)


def test_a_child_on_a_cycle_is_not_drawn_beside_the_subject():
    kinds = [kind("a"), kind("b", "a"), kind("c", "d"), kind("d", "c")]
    assert tree.neighbourhood(kinds, 0).children == (1,)
