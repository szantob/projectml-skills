"""Whether a document fits the contract's schema.

The schema is read from the contract, never restated here: the contract is the
one statement of the written shape, shared with the editor.
"""

import json
from pathlib import Path

import jsonschema

CONTRACT = Path(__file__).resolve().parent.parent / "contract"

_SCHEMA = json.loads((CONTRACT / "package.schema.json").read_text(encoding="utf-8"))

# The schema says which draft it is written against, so it is asked rather than
# assumed. Naming a draft here would go on meaning the old one after the
# contract moved to a newer draft, and nothing would fail to say so.
_VALIDATOR = jsonschema.validators.validator_for(_SCHEMA)(_SCHEMA)


def _where(error):
    path = "/".join(str(part) for part in error.absolute_path)
    return path or "(the package)"


def _order(error):
    # Strings and integers are kept apart so that a path through a list never
    # has its index compared with a key.
    return [(isinstance(part, str), part) for part in error.absolute_path]


def misfits(document):
    """Each place ``document`` departs from the schema, one line apiece.

    Empty when the document fits. Each line starts with where the misfit is — a
    path such as ``kinds/0`` — and then says what is wrong there.
    """
    errors = sorted(_VALIDATOR.iter_errors(document), key=_order)
    return [f"{_where(error)}: {error.message}" for error in errors]
