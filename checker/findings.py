"""Issues and gaps: the checker's findings, written from the contract alone.

An issue is something wrong with a package; the command exits non-zero when
one is raised. A gap is prose the notation allows to be left blank, and the
package has left blank; a gap alone changes nothing about the exit status.

Both are described in ``contract/vocabulary.json``: the issue codes, the gap
fields, and a gloss for each saying exactly when it is reported and how
often. This module reports nothing that gloss does not call for, and reports
everything it does.
"""

import re
from dataclasses import dataclass

_PLACEHOLDER = re.compile(r"\{([^{}]*)\}")


@dataclass(frozen=True)
class Issue:
    code: str
    kind: str | None
    message: str


@dataclass(frozen=True)
class Gap:
    kind: str
    field: str
    parameter: str | None


def _blank(text):
    """Whether ``text`` counts as unwritten: empty, or whitespace only."""
    return text.strip() == ""


def _repeated(values):
    """The values occurring more than once among ``values``, each returned
    once, in the order its second occurrence is met."""
    seen = set()
    repeats = []
    for value in values:
        if value in seen:
            if value not in repeats:
                repeats.append(value)
        else:
            seen.add(value)
    return repeats


def _placeholders(text):
    """The distinct, non-empty placeholder names in a wording template.

    A placeholder is written ``{name}``; the whitespace inside the braces is
    trimmed, and an empty placeholder is ignored.
    """
    names = []
    seen = set()
    for match in _PLACEHOLDER.finditer(text):
        name = match.group(1).strip()
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def _specialisation_edges(kinds):
    """For each kind, by its position in ``kinds``, the positions of the
    kinds that carry the identity it specialises."""
    positions = {}
    for position, kind in enumerate(kinds):
        positions.setdefault(kind["id"], []).append(position)
    return [
        [] if kind["specialises"] is None else positions.get(kind["specialises"], [])
        for kind in kinds
    ]


def _on_a_cycle(edges, start):
    """Whether following ``edges`` from ``start`` can lead back to
    ``start``."""
    stack = list(edges[start])
    visited = set()
    while stack:
        position = stack.pop()
        if position == start:
            return True
        if position in visited:
            continue
        visited.add(position)
        stack.extend(edges[position])
    return False


def issues(package):
    """Every issue ``package`` raises, per the contract's vocabulary."""
    kinds = package["kinds"]
    found = []

    for identity in _repeated(domain["id"] for domain in package["valueDomains"]):
        found.append(
            Issue(
                "duplicate-value-domain-id",
                None,
                f"The value domain identity {identity!r} is declared more than once.",
            )
        )

    for identity in _repeated(kind["id"] for kind in kinds):
        found.append(
            Issue(
                "duplicate-kind-id",
                identity,
                f"The identity {identity!r} is carried by more than one kind.",
            )
        )

    known_kind_ids = {kind["id"] for kind in kinds}
    known_domain_ids = {domain["id"] for domain in package["valueDomains"]}

    for kind in kinds:
        kind_id = kind["id"]
        parameters = kind["parameters"]
        rules = kind["rules"]

        for name in _repeated(parameter["name"] for parameter in parameters):
            found.append(
                Issue(
                    "duplicate-parameter-name",
                    kind_id,
                    f"The parameter {name!r} is declared more than once.",
                )
            )

        for parameter in parameters:
            if parameter["valueDomainId"] not in known_domain_ids:
                found.append(
                    Issue(
                        "unknown-value-domain",
                        kind_id,
                        f"The parameter {parameter['name']!r} names a value domain "
                        "that is not declared.",
                    )
                )

        placeholders = _placeholders(kind["text"])
        parameter_names = {parameter["name"] for parameter in parameters}

        for name in placeholders:
            if name not in parameter_names:
                found.append(
                    Issue(
                        "placeholder-without-parameter",
                        kind_id,
                        f"The wording template names a placeholder {{{name}}} that "
                        "is not a declared parameter.",
                    )
                )

        for parameter in parameters:
            if parameter["name"] not in placeholders:
                found.append(
                    Issue(
                        "parameter-without-placeholder",
                        kind_id,
                        f"The parameter {parameter['name']!r} appears in no "
                        "placeholder of the wording template.",
                    )
                )

        for identity in _repeated(rule["id"] for rule in rules):
            found.append(
                Issue(
                    "duplicate-rule-id",
                    kind_id,
                    f"The rule identity {identity!r} is declared more than once.",
                )
            )

        for rule in rules:
            if rule["type"] == "CompletenessRule" and (
                rule["implies"] is None or rule["implies"] not in known_kind_ids
            ):
                found.append(
                    Issue(
                        "unknown-implied-definition",
                        kind_id,
                        f"The rule {rule['id']!r} implies no kind that exists.",
                    )
                )

    edges = _specialisation_edges(kinds)
    for position, kind in enumerate(kinds):
        parent = kind["specialises"]
        if parent is None:
            continue
        if _on_a_cycle(edges, position):
            found.append(
                Issue(
                    "specialisation-cycle",
                    kind["id"],
                    f"The kind {kind['id']!r} sits on a specialisation cycle.",
                )
            )
        elif parent not in known_kind_ids:
            found.append(
                Issue(
                    "unknown-parent",
                    kind["id"],
                    f"The kind {kind['id']!r} specialises {parent!r}, which no "
                    "kind carries.",
                )
            )

    return found


def gaps(package):
    """Every gap ``package`` leaves, per the contract's vocabulary.

    Gaps come in the order the file holds them: kinds as they appear, and
    within a kind its attributes in the order the written shape lists them.
    """
    found = []
    for kind in package["kinds"]:
        kind_id = kind["id"]

        if _blank(kind["name"]):
            found.append(Gap(kind_id, "name", None))
        if _blank(kind["text"]):
            found.append(Gap(kind_id, "text", None))
        if _blank(kind["whenItApplies"]):
            found.append(Gap(kind_id, "whenItApplies", None))

        for parameter in kind["parameters"]:
            if _blank(parameter["whatToAsk"]):
                found.append(Gap(kind_id, "whatToAsk", parameter["name"]))

        for rule in kind["rules"]:
            if _blank(rule["whenItApplies"]):
                found.append(Gap(kind_id, "ruleWhenItApplies", None))
            if _blank(rule["whatToLookFor"]):
                found.append(Gap(kind_id, "ruleWhatToLookFor", None))

        if _blank(kind["howItWouldBeVerified"]):
            found.append(Gap(kind_id, "howItWouldBeVerified", None))
        if _blank(kind["wordingRule"]):
            found.append(Gap(kind_id, "wordingRule", None))

    return found
