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

from tree import on_a_cycle, parameters_had, specialisation_edges

_PLACEHOLDER = re.compile(r"\{([^{}]*)\}")

# The operations each level of comparability defines (ProjectML K101): an
# ordered domain is comparable for equality too.
_EQUALITY = {"equals", "isOneOf"}
_ORDERINGS = {"lessThan", "atMost", "greaterThan", "atLeast"}
ALLOWED_OPERATIONS = {
    "notComparable": set(),
    "equality": _EQUALITY,
    "ordered": _EQUALITY | _ORDERINGS,
}


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


# Whitespace, as the contract defines it. Not what ``str.strip`` calls
# whitespace with no argument: that follows Unicode, the other implementation
# follows its own language, and the two do not agree.
WHITESPACE = " \t\r\n"


def _blank(text):
    """Whether ``text`` counts as unwritten: empty, or whitespace only."""
    return text.strip(WHITESPACE) == ""


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
        name = match.group(1).strip(WHITESPACE)
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names


def _clashes(own, inherited):
    """The values among ``own`` that another of ``own``, or one of
    ``inherited``, also carries - each once, in the order first met.

    This is how a clash between parameters is reported on the kind that
    declares one of them, and not again on every descendant."""
    found = []
    for value in own:
        if value in found:
            continue
        if own.count(value) + inherited.count(value) > 1:
            found.append(value)
    return found


def _constant_unwritten(constant):
    if isinstance(constant, list):
        return not constant or any(_blank(entry) for entry in constant)
    return _blank(constant)


def issues(package):
    """Every issue ``package`` raises, per the contract's vocabulary."""
    kinds = package["kinds"]
    domains = package["valueDomains"]
    found = []

    for identity in _repeated(domain["id"] for domain in domains):
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

    # A name is compared trimmed and otherwise exactly. An unwritten name is a
    # gap, so it is left out here: two kinds without a name share nothing.
    written_names = [
        kind["name"].strip(WHITESPACE) for kind in kinds if not _blank(kind["name"])
    ]
    shared_names = set(_repeated(written_names))
    for kind in kinds:
        name = kind["name"].strip(WHITESPACE)
        if name in shared_names:
            found.append(
                Issue(
                    "duplicate-kind-name",
                    kind["id"],
                    f"The name {name!r} is carried by more than one kind.",
                )
            )

    known_kind_ids = {kind["id"] for kind in kinds}
    known_domain_ids = {domain["id"] for domain in domains}

    for position, kind in enumerate(kinds):
        kind_id = kind["id"]
        parameters = kind["parameters"]
        rules = kind["rules"]
        had = [parameter for _, parameter in parameters_had(kinds, position)]
        inherited = had[len(parameters):]

        for identity in _clashes(
            [p["id"] for p in parameters], [p["id"] for p in inherited]
        ):
            found.append(
                Issue(
                    "duplicate-parameter-id",
                    kind_id,
                    f"The parameter identity {identity!r} is carried by another "
                    "parameter this kind declares or inherits.",
                )
            )

        def written(group):
            return [
                p["name"].strip(WHITESPACE) for p in group if not _blank(p["name"])
            ]

        for name in _clashes(written(parameters), written(inherited)):
            found.append(
                Issue(
                    "duplicate-parameter-name",
                    kind_id,
                    f"The parameter name {name!r} is carried by another parameter "
                    "this kind declares or inherits.",
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

        if kind["abstract"]:
            if not _blank(kind["text"]):
                found.append(
                    Issue(
                        "template-on-abstract-kind",
                        kind_id,
                        "The kind is abstract, so nothing is produced under it, and "
                        "it carries a wording template.",
                    )
                )
        else:
            placeholders = _placeholders(kind["text"])
            names_had = set(written(had))

            for name in placeholders:
                if name not in names_had:
                    found.append(
                        Issue(
                            "placeholder-without-parameter",
                            kind_id,
                            f"The wording template names a placeholder {{{name}}} "
                            "that is no parameter this kind has.",
                        )
                    )

            for parameter in had:
                name = parameter["name"].strip(WHITESPACE)
                if name and name not in placeholders:
                    found.append(
                        Issue(
                            "parameter-without-placeholder",
                            kind_id,
                            f"The parameter {name!r} appears in no placeholder of "
                            "the wording template.",
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

            for criterion in rule["guard"]:
                named = criterion["parameter"]
                matches = [p for p in had if p["id"] == named]
                if named is None or not matches:
                    found.append(
                        Issue(
                            "unknown-guard-parameter",
                            kind_id,
                            f"A criterion of the rule {rule['id']!r} names "
                            f"{named!r}, which is no parameter this kind has.",
                        )
                    )
                    continue
                if len(matches) > 1:
                    continue
                carrying = [
                    d for d in domains if d["id"] == matches[0]["valueDomainId"]
                ]
                if len(carrying) != 1:
                    continue
                comparability = carrying[0]["comparability"]
                if criterion["operation"] not in ALLOWED_OPERATIONS[comparability]:
                    found.append(
                        Issue(
                            "guard-operation-not-allowed",
                            kind_id,
                            f"A criterion of the rule {rule['id']!r} applies "
                            f"{criterion['operation']} to the parameter "
                            f"{matches[0]['name']!r}, whose value domain is "
                            f"{comparability}.",
                        )
                    )

    edges = specialisation_edges(kinds)
    for position, kind in enumerate(kinds):
        parent = kind["specialises"]
        if parent is None:
            continue
        if on_a_cycle(edges, position):
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
    An abstract kind carries no template, and neither its verification
    method nor its wording rule applies to it, so none of the three is a gap
    there.
    """
    found = []
    for kind in package["kinds"]:
        kind_id = kind["id"]
        concrete = not kind["abstract"]

        if _blank(kind["name"]):
            found.append(Gap(kind_id, "name", None))
        if concrete and _blank(kind["text"]):
            found.append(Gap(kind_id, "text", None))
        if _blank(kind["whenItApplies"]):
            found.append(Gap(kind_id, "whenItApplies", None))

        for parameter in kind["parameters"]:
            if _blank(parameter["name"]):
                found.append(Gap(kind_id, "parameterName", parameter["id"]))
            if _blank(parameter["whatToAsk"]):
                found.append(Gap(kind_id, "whatToAsk", parameter["id"]))

        for rule in kind["rules"]:
            for criterion in rule["guard"]:
                if _constant_unwritten(criterion["constant"]):
                    found.append(
                        Gap(kind_id, "guardConstant", criterion["parameter"])
                    )
            if _blank(rule["whenItApplies"]):
                found.append(Gap(kind_id, "ruleWhenItApplies", None))
            if _blank(rule["whatToLookFor"]):
                found.append(Gap(kind_id, "ruleWhatToLookFor", None))

        if concrete and _blank(kind["howItWouldBeVerified"]):
            found.append(Gap(kind_id, "howItWouldBeVerified", None))
        if concrete and _blank(kind["wordingRule"]):
            found.append(Gap(kind_id, "wordingRule", None))

    return found
