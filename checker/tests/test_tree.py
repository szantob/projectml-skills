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
    assert near.parent_cyclic is None
    assert near.children == ()


def test_a_child_names_its_parent_s_position():
    near = tree.neighbourhood([kind("a"), kind("b", "a")], 1)
    assert near.parent == 0
    assert near.parent_missing is False
    assert near.parent_cyclic is None


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
    assert near.parent_cyclic is None


def test_a_parent_that_sits_on_a_cycle_is_named_rather_than_missing():
    # "a" and "b" specialise each other, a cycle; "c" descends from "a" but
    # is not on the cycle itself. The parent identity is carried — by a kind
    # that has no place in a tree — so this is not the same state as a
    # parent no kind carries at all.
    kinds = [kind("a", "b"), kind("b", "a"), kind("c", "a")]
    near = tree.neighbourhood(kinds, 2)
    assert near.parent is None
    assert near.parent_missing is False
    assert near.parent_cyclic == 0
    assert near.children == ()


def test_a_subject_on_a_cycle_is_refused():
    with pytest.raises(tree.NotDrawable, match="cycle"):
        tree.neighbourhood([kind("a", "a")], 0)


def test_a_subject_on_a_cycle_cites_the_finding():
    with pytest.raises(tree.NotDrawable, match="specialisation-cycle"):
        tree.neighbourhood([kind("a", "a")], 0)


def test_subject_ambiguity_is_counted_over_cyclic_carriers_too():
    # "p" and "q" specialise each other, a cycle; a second, non-cyclic kind
    # also carries "p". Filtering cyclic carriers before counting would call
    # this subject unambiguous, hiding one of the two kinds called "p" the
    # way diagram.py used to before its own fix.
    kinds = [kind("p", "q"), kind("q", "p"), kind("p")]
    with pytest.raises(tree.NotDrawable, match="2 kinds"):
        tree.neighbourhood(kinds, 2)


def test_parent_ambiguity_is_counted_over_cyclic_carriers_too():
    kinds = [kind("p", "q"), kind("q", "p"), kind("p"), kind("s", "p")]
    with pytest.raises(tree.NotDrawable, match="2 kinds"):
        tree.neighbourhood(kinds, 3)


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
