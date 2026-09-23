"""Each operation's guarantee, each refusal, and the candidates each returns.

Every package here is invented.
"""

import copy
import uuid

import pytest

import contract_schema
import operations
from operations import Refused


def kind(identity, parent=None, name=None, **prose):
    return {
        "id": identity,
        "name": identity.title() if name is None else name,
        "text": prose.get("text", ""),
        "whenItApplies": prose.get("whenItApplies", ""),
        "parameters": prose.get("parameters", []),
        "rules": prose.get("rules", []),
        "howItWouldBeVerified": prose.get("howItWouldBeVerified", ""),
        "wordingRule": prose.get("wordingRule", ""),
        "specialises": parent,
    }


def package(*kinds, domains=()):
    return {
        "schemaVersion": 3,
        "name": "Stage equipment",
        "version": "",
        "valueDomains": list(domains),
        "kinds": list(kinds),
    }


def domain(identity):
    return {"id": identity, "name": identity, "description": ""}


def parameter(name, domain_id):
    return {"name": name, "valueDomainId": domain_id, "whatToAsk": ""}


def rule(identity, implies):
    return {
        "id": identity,
        "type": "CompletenessRule",
        "inForce": True,
        "whenItApplies": "",
        "whatToLookFor": "",
        "implies": implies,
    }


def ids(document):
    return [k["id"] for k in document["kinds"]]


def by_id(document, identity):
    (found,) = [k for k in document["kinds"] if k["id"] == identity]
    return found


# stage
#   lighting
#     fixture
#       moving-head
#   screen
#     led-wall
SAMPLE = package(
    kind("stage"),
    kind("lighting", "stage", "Lighting", text="Lighting on the stage."),
    kind("fixture", "lighting", "Fixture", text="A lighting fixture."),
    kind("moving-head", "fixture", "Moving head", text="A moving-head Fixture."),
    kind("screen", "stage", "Screen"),
    kind("led-wall", "screen", "LED wall", text="The Screen is an LED wall."),
)


@pytest.fixture
def sample():
    return copy.deepcopy(SAMPLE)


# -- resolving a subject ------------------------------------------------------


def test_an_identity_no_kind_carries_is_refused(sample):
    with pytest.raises(Refused, match="No kind carries"):
        operations.delete(sample, "nothing")


def test_an_identity_two_kinds_carry_is_refused(sample):
    sample["kinds"].append(kind("screen", None, "Another screen"))
    with pytest.raises(Refused, match="carried by 2 kinds"):
        operations.delete(sample, "screen")


def test_a_subtree_whose_member_shares_its_identity_is_refused(sample):
    # Whose children the kinds naming "fixture" are cannot be decided, so the
    # subtree under "lighting" cannot be either.
    sample["kinds"].append(kind("fixture", None, "Unrelated"))
    with pytest.raises(Refused, match="'fixture'"):
        operations.move(sample, "lighting", None)


def test_a_kind_on_a_cycle_has_no_subtree(sample):
    sample["kinds"] += [kind("a", "b"), kind("b", "a")]
    with pytest.raises(Refused, match="cycle"):
        operations.delete(sample, "a")


def test_no_operation_changes_the_document_it_was_given(sample):
    operations.move(sample, "fixture", "screen")
    operations.delete(sample, "lighting")
    operations.set_attribute(sample, "screen", "name", "Display")
    operations.create(sample, "screen", "Projector")
    operations.extract(sample, "fixture")
    assert sample == SAMPLE


# -- move -----------------------------------------------------------------------


def test_move_changes_only_the_roots_parent(sample):
    result = operations.move(sample, "fixture", "screen")
    expected = copy.deepcopy(SAMPLE)
    by_id(expected, "fixture")["specialises"] = "screen"
    assert result.document == expected


def test_move_to_the_root_level(sample):
    result = operations.move(sample, "screen", None)
    assert by_id(result.document, "screen")["specialises"] is None


def test_move_under_its_own_descendant_is_refused(sample):
    with pytest.raises(Refused, match="inside the subtree"):
        operations.move(sample, "lighting", "moving-head")


def test_move_under_itself_is_refused(sample):
    with pytest.raises(Refused, match="inside the subtree"):
        operations.move(sample, "lighting", "lighting")


def test_move_to_an_ambiguous_target_is_refused(sample):
    sample["kinds"].append(kind("screen", None, "Another screen"))
    with pytest.raises(Refused, match="carried by 2 kinds"):
        operations.move(sample, "fixture", "screen")


def test_move_to_where_it_already_is_changes_nothing(sample):
    result = operations.move(sample, "fixture", "lighting")
    assert result.changed is False
    assert result.document == SAMPLE


def test_move_names_both_ancestor_chains(sample):
    result = operations.move(sample, "fixture", "screen")
    (arrival,) = [c for c in result.candidates if "arrived" in c]
    assert "Stage > Lighting" in arrival
    assert "Stage > Screen" in arrival
    assert "2 kinds" in arrival


def test_move_finds_prose_naming_an_ancestor_it_no_longer_has(sample):
    result = operations.move(sample, "fixture", "screen")
    mentions = [c for c in result.candidates if "mentions" in c]
    # "Lighting" is lost; "Stage" is kept, so it is not a candidate.
    assert mentions == [
        "kind 'fixture' (Fixture), text: mentions 'Lighting', "
        "an ancestor it no longer has."
    ]


def test_mention_is_matched_at_a_word_start_whatever_the_case(sample):
    by_id(sample, "moving-head")["text"] = "Not for lightingless rigs."
    result = operations.move(sample, "fixture", "screen")
    assert any("'moving-head'" in c and "'Lighting'" in c for c in result.candidates)
    by_id(sample, "moving-head")["text"] = "Not for highlighting."
    result = operations.move(sample, "fixture", "screen")
    assert not any("'moving-head'" in c for c in result.candidates if "mentions" in c)


# -- delete ---------------------------------------------------------------------


def test_delete_removes_the_whole_subtree(sample):
    result = operations.delete(sample, "lighting")
    assert ids(result.document) == ["stage", "screen", "led-wall"]


def test_delete_leaves_no_specialises_dangling(sample):
    result = operations.delete(sample, "lighting")
    carried = set(ids(result.document))
    assert all(
        k["specialises"] is None or k["specialises"] in carried
        for k in result.document["kinds"]
    )


def test_delete_reports_a_rule_outside_implying_a_deleted_kind(sample):
    by_id(sample, "screen")["rules"] = [rule("needs-light", "fixture")]
    result = operations.delete(sample, "lighting")
    assert any("needs-light" in n and "'fixture'" in n for n in result.notes)
    # Reported, not dropped: the rule is still there.
    assert by_id(result.document, "screen")["rules"] == [rule("needs-light", "fixture")]


def test_delete_finds_prose_outside_mentioning_a_deleted_kind(sample):
    by_id(sample, "led-wall")["howItWouldBeVerified"] = "Measured under a Fixture."
    result = operations.delete(sample, "lighting")
    assert any(
        "'led-wall'" in c and "howItWouldBeVerified" in c and "'Fixture'" in c
        for c in result.candidates
    )


# -- set ------------------------------------------------------------------------


def test_set_changes_only_that_attribute(sample):
    result = operations.set_attribute(sample, "screen", "text", "New text.")
    expected = copy.deepcopy(SAMPLE)
    by_id(expected, "screen")["text"] = "New text."
    assert result.document == expected


@pytest.mark.parametrize("attribute", ["id", "specialises", "parameters", "rules"])
def test_set_refuses_what_is_not_prose(sample, attribute):
    with pytest.raises(Refused):
        operations.set_attribute(sample, "screen", attribute, "x")


def test_set_refuses_an_attribute_the_schema_does_not_have(sample):
    with pytest.raises(Refused):
        operations.set_attribute(sample, "screen", "colour", "x")


def test_renaming_finds_prose_still_using_the_old_name(sample):
    result = operations.set_attribute(sample, "screen", "name", "Display")
    assert any("'led-wall'" in c and "'Screen'" in c for c in result.candidates)
    # Its own name field is the one that changed; it is no candidate.
    assert not any("'screen'" in c and ", name:" in c for c in result.candidates)


def test_setting_the_same_value_changes_nothing(sample):
    result = operations.set_attribute(sample, "screen", "name", "Screen")
    assert result.changed is False


# -- create ---------------------------------------------------------------------


def test_create_adds_one_leaf_with_a_uuid(sample):
    result = operations.create(sample, "screen", "Projector")
    assert result.document["kinds"][:-1] == SAMPLE["kinds"]
    new = result.document["kinds"][-1]
    assert str(uuid.UUID(new["id"])) == new["id"] == result.created
    assert new["specialises"] == "screen"
    assert new["name"] == "Projector"
    assert contract_schema.misfits(result.document) == []


def test_create_at_the_root_level(sample):
    result = operations.create(sample, None, "")
    assert result.document["kinds"][-1]["specialises"] is None


def test_create_under_an_ambiguous_parent_is_refused(sample):
    sample["kinds"].append(kind("screen", None, "Another screen"))
    with pytest.raises(Refused):
        operations.create(sample, "screen", "Projector")


# -- extract ----------------------------------------------------------------------


def test_extract_holds_the_ancestor_chain_and_the_subtree(sample):
    result = operations.extract(sample, "fixture")
    assert ids(result.document) == ["stage", "lighting", "fixture", "moving-head"]


def test_extract_takes_only_the_value_domains_its_kinds_use(sample):
    sample["valueDomains"] = [domain("watts"), domain("pixels"), domain("unused")]
    by_id(sample, "lighting")["parameters"] = [parameter("power", "watts")]
    by_id(sample, "led-wall")["parameters"] = [parameter("pitch", "pixels")]
    result = operations.extract(sample, "fixture")
    assert [d["id"] for d in result.document["valueDomains"]] == ["watts"]


def test_extract_notes_a_rule_implying_a_kind_left_out(sample):
    by_id(sample, "fixture")["rules"] = [rule("needs-screen", "screen")]
    result = operations.extract(sample, "fixture")
    assert any("needs-screen" in n and "'screen'" in n for n in result.notes)


def test_extract_notes_where_the_ancestor_chain_breaks(sample):
    by_id(sample, "lighting")["specialises"] = "gone"
    result = operations.extract(sample, "fixture")
    assert ids(result.document) == ["lighting", "fixture", "moving-head"]
    assert any("'gone'" in n for n in result.notes)


def test_an_extract_fits_the_schema(sample):
    extracted = operations.extract(sample, "led-wall").document
    assert contract_schema.misfits(extracted) == []
