"""The schema step: the contract's own schema, applied by jsonschema."""

import contract_schema


def _kind(**changes):
    kind = {
        "id": "00000000-0000-4000-8000-000000000001",
        "name": "A",
        "text": "shall hold",
        "whenItApplies": "Always.",
        "parameters": [],
        "rules": [],
        "howItWouldBeVerified": "By inspection.",
        "wordingRule": "One sentence.",
        "specialises": None,
    }
    kind.update(changes)
    return kind


def _package(*kinds):
    return {
        "schemaVersion": 4,
        "name": "A package",
        "version": "",
        "valueDomains": [],
        "kinds": list(kinds),
    }


def test_the_schema_is_the_contracts_own():
    assert (contract_schema.CONTRACT / "package.schema.json").is_file()


def test_a_package_that_fits_has_no_misfits():
    assert contract_schema.misfits(_package(_kind())) == []


def test_a_misfit_says_where_it_is():
    wrong = contract_schema.misfits(_package(_kind(notes="an attribute of its own")))
    assert len(wrong) == 1
    assert wrong[0].startswith("kinds/0: ")
    assert "notes" in wrong[0]


def test_a_misfit_at_the_top_names_the_package():
    wrong = contract_schema.misfits({**_package(), "schemaVersion": 3})
    assert wrong == ["schemaVersion: 4 was expected"]


def test_a_document_that_is_not_a_mapping_does_not_fit():
    assert contract_schema.misfits(None) != []


def test_a_kind_identity_must_be_a_uuid():
    wrong = contract_schema.misfits(_package(_kind(id="capacity")))
    assert len(wrong) == 1 and wrong[0].startswith("kinds/0/id:")


def test_a_uppercase_uuid_is_not_one():
    wrong = contract_schema.misfits(
        _package(_kind(id="00000000-0000-4000-8000-00000000000A"))
    )
    assert len(wrong) == 1 and wrong[0].startswith("kinds/0/id:")


def test_a_parent_must_be_a_uuid_or_null():
    wrong = contract_schema.misfits(_package(_kind(specialises="capacity")))
    assert len(wrong) == 1 and wrong[0].startswith("kinds/0/specialises:")
