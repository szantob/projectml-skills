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
        "schemaVersion": 4,
        "name": "Building services",
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


# building
#   heating
#     radiator
#       valve
#   ventilation
#     air-handler
SAMPLE = package(
    kind("building"),
    kind("heating", "building", "Heating", text="Heating in the building."),
    kind("radiator", "heating", "Radiator", text="A heating radiator."),
    kind("valve", "radiator", "Thermostatic valve", text="A Radiator's valve."),
    kind("ventilation", "building", "Ventilation"),
    kind("air-handler", "ventilation", "Air handler", text="Part of the Ventilation."),
)


@pytest.fixture
def sample():
    return copy.deepcopy(SAMPLE)


# The sample's identities are readable words, not UUIDs: no operation depends
# on what an identity looks like, and the tests read better for it. A test
# that holds a result to the schema uses this one instead.
ROOT = "00000000-0000-4000-8000-000000000001"
LEAF = "00000000-0000-4000-8000-000000000002"


@pytest.fixture
def valid():
    return package(kind(ROOT, None, "Building"), kind(LEAF, ROOT, "Ventilation"))


# -- resolving a subject ------------------------------------------------------


def test_an_identity_no_kind_carries_is_refused(sample):
    with pytest.raises(Refused, match="No kind carries"):
        operations.delete(sample, "nothing")


def test_an_identity_two_kinds_carry_is_refused(sample):
    sample["kinds"].append(kind("ventilation", None, "Another ventilation"))
    with pytest.raises(Refused, match="carried by 2 kinds"):
        operations.delete(sample, "ventilation")


def test_a_subtree_whose_member_shares_its_identity_is_refused(sample):
    # Whose children the kinds naming "radiator" are cannot be decided, so the
    # subtree under "heating" cannot be either.
    sample["kinds"].append(kind("radiator", None, "Unrelated"))
    with pytest.raises(Refused, match="'radiator'"):
        operations.move(sample, "heating", None)


def test_a_kind_on_a_cycle_has_no_subtree(sample):
    sample["kinds"] += [kind("a", "b"), kind("b", "a")]
    with pytest.raises(Refused, match="cycle"):
        operations.delete(sample, "a")


def test_no_operation_changes_the_document_it_was_given(sample):
    operations.move(sample, "radiator", "ventilation")
    operations.delete(sample, "heating")
    operations.set_attribute(sample, "ventilation", "name", "Airflow")
    operations.create(sample, "ventilation", "Extractor fan")
    operations.extract(sample, "radiator")
    assert sample == SAMPLE


# -- move -----------------------------------------------------------------------


def test_move_changes_only_the_roots_parent(sample):
    result = operations.move(sample, "radiator", "ventilation")
    expected = copy.deepcopy(SAMPLE)
    by_id(expected, "radiator")["specialises"] = "ventilation"
    assert result.document == expected


def test_move_to_the_root_level(sample):
    result = operations.move(sample, "ventilation", None)
    assert by_id(result.document, "ventilation")["specialises"] is None


def test_move_under_its_own_descendant_is_refused(sample):
    with pytest.raises(Refused, match="inside the subtree"):
        operations.move(sample, "heating", "valve")


def test_move_under_itself_is_refused(sample):
    with pytest.raises(Refused, match="inside the subtree"):
        operations.move(sample, "heating", "heating")


def test_move_to_an_ambiguous_target_is_refused(sample):
    sample["kinds"].append(kind("ventilation", None, "Another ventilation"))
    with pytest.raises(Refused, match="carried by 2 kinds"):
        operations.move(sample, "radiator", "ventilation")


def test_move_to_where_it_already_is_changes_nothing(sample):
    result = operations.move(sample, "radiator", "heating")
    assert result.changed is False
    assert result.document == SAMPLE


def test_move_names_both_ancestor_chains(sample):
    result = operations.move(sample, "radiator", "ventilation")
    (arrival,) = [c for c in result.candidates if "arrived" in c]
    assert "Building > Heating" in arrival
    assert "Building > Ventilation" in arrival
    assert "2 kinds" in arrival


def test_move_finds_prose_naming_an_ancestor_it_no_longer_has(sample):
    result = operations.move(sample, "radiator", "ventilation")
    mentions = [c for c in result.candidates if "mentions" in c]
    # "Heating" is lost; "Building" is kept, so it is not a candidate.
    assert mentions == [
        "kind 'radiator' (Radiator), text: mentions 'Heating', "
        "an ancestor it no longer has."
    ]


def test_mention_is_matched_at_a_word_start_whatever_the_case(sample):
    by_id(sample, "valve")["text"] = "Not for heatingless rooms."
    result = operations.move(sample, "radiator", "ventilation")
    assert any("'valve'" in c and "'Heating'" in c for c in result.candidates)
    by_id(sample, "valve")["text"] = "Not for preheating."
    result = operations.move(sample, "radiator", "ventilation")
    assert not any("'valve'" in c for c in result.candidates if "mentions" in c)


# -- delete ---------------------------------------------------------------------


def test_delete_removes_the_whole_subtree(sample):
    result = operations.delete(sample, "heating")
    assert ids(result.document) == ["building", "ventilation", "air-handler"]


def test_delete_leaves_no_specialises_dangling(sample):
    result = operations.delete(sample, "heating")
    carried = set(ids(result.document))
    assert all(
        k["specialises"] is None or k["specialises"] in carried
        for k in result.document["kinds"]
    )


def test_delete_reports_a_rule_outside_implying_a_deleted_kind(sample):
    by_id(sample, "ventilation")["rules"] = [rule("needs-heat", "radiator")]
    result = operations.delete(sample, "heating")
    assert any("needs-heat" in n and "'radiator'" in n for n in result.notes)
    # Reported, not dropped: the rule is still there.
    kept = by_id(result.document, "ventilation")["rules"]
    assert kept == [rule("needs-heat", "radiator")]


def test_delete_finds_prose_outside_mentioning_a_deleted_kind(sample):
    by_id(sample, "air-handler")["howItWouldBeVerified"] = "Measured beside a Radiator."
    result = operations.delete(sample, "heating")
    assert any(
        "'air-handler'" in c and "howItWouldBeVerified" in c and "'Radiator'" in c
        for c in result.candidates
    )


# -- set ------------------------------------------------------------------------


def test_set_changes_only_that_attribute(sample):
    result = operations.set_attribute(sample, "ventilation", "text", "New text.")
    expected = copy.deepcopy(SAMPLE)
    by_id(expected, "ventilation")["text"] = "New text."
    assert result.document == expected


@pytest.mark.parametrize("attribute", ["id", "specialises", "parameters", "rules"])
def test_set_refuses_what_is_not_prose(sample, attribute):
    with pytest.raises(Refused):
        operations.set_attribute(sample, "ventilation", attribute, "x")


def test_set_refuses_an_attribute_the_schema_does_not_have(sample):
    with pytest.raises(Refused):
        operations.set_attribute(sample, "ventilation", "colour", "x")


def test_renaming_finds_prose_still_using_the_old_name(sample):
    result = operations.set_attribute(sample, "ventilation", "name", "Airflow")
    assert any("'air-handler'" in c and "'Ventilation'" in c for c in result.candidates)
    # Its own name field is the one that changed; it is no candidate.
    assert not any("'ventilation'" in c and ", name:" in c for c in result.candidates)


def test_setting_the_same_value_changes_nothing(sample):
    result = operations.set_attribute(sample, "ventilation", "name", "Ventilation")
    assert result.changed is False


# -- create ---------------------------------------------------------------------


def test_create_adds_one_leaf_with_a_uuid(valid):
    result = operations.create(valid, LEAF, "Extractor fan")
    assert result.document["kinds"][:-1] == valid["kinds"]
    new = result.document["kinds"][-1]
    assert str(uuid.UUID(new["id"])) == new["id"] == result.created
    assert uuid.UUID(new["id"]).version == 4
    assert new["specialises"] == LEAF
    assert new["name"] == "Extractor fan"
    assert contract_schema.misfits(result.document) == []


def test_create_at_the_root_level(sample):
    result = operations.create(sample, None, "")
    assert result.document["kinds"][-1]["specialises"] is None


def test_create_under_an_ambiguous_parent_is_refused(sample):
    sample["kinds"].append(kind("ventilation", None, "Another ventilation"))
    with pytest.raises(Refused):
        operations.create(sample, "ventilation", "Extractor fan")


# -- extract ----------------------------------------------------------------------


def test_extract_holds_the_ancestor_chain_and_the_subtree(sample):
    result = operations.extract(sample, "radiator")
    assert ids(result.document) == ["building", "heating", "radiator", "valve"]


def test_extract_takes_only_the_value_domains_its_kinds_use(sample):
    sample["valueDomains"] = [
        domain("kilowatts"),
        domain("cubic-metres"),
        domain("unused"),
    ]
    by_id(sample, "heating")["parameters"] = [parameter("output", "kilowatts")]
    by_id(sample, "air-handler")["parameters"] = [parameter("airflow", "cubic-metres")]
    result = operations.extract(sample, "radiator")
    assert [d["id"] for d in result.document["valueDomains"]] == ["kilowatts"]


def test_extract_notes_a_rule_implying_a_kind_left_out(sample):
    by_id(sample, "radiator")["rules"] = [rule("needs-ventilation", "ventilation")]
    result = operations.extract(sample, "radiator")
    assert any("needs-ventilation" in n and "'ventilation'" in n for n in result.notes)


def test_extract_notes_where_the_ancestor_chain_breaks(sample):
    by_id(sample, "heating")["specialises"] = "gone"
    result = operations.extract(sample, "radiator")
    assert ids(result.document) == ["heating", "radiator", "valve"]
    assert any("'gone'" in n for n in result.notes)


def test_an_extract_fits_the_schema(valid):
    extracted = operations.extract(valid, LEAF).document
    assert contract_schema.misfits(extracted) == []
