"""The schema step: the contract's own schema, applied by jsonschema."""

import contract_schema


def _kind(**changes):
    kind = {
        "id": "a",
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
        "schemaVersion": 3,
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
    wrong = contract_schema.misfits({**_package(), "schemaVersion": 2})
    assert wrong == ["schemaVersion: 3 was expected"]


def test_a_document_that_is_not_a_mapping_does_not_fit():
    assert contract_schema.misfits(None) != []
