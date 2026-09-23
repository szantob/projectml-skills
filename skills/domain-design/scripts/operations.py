"""The editing operations, as functions from a package to a package.

No reading and no writing here: each operation takes a document, returns a
new one, and never changes the one it was given. ``edit.py`` does the I/O.

**An operation carries what it moves.** A moved kind keeps every attribute
it had; only the one ``specialises`` that says where the subtree hangs
changes. That is the point of having operations at all: rebuilding a
skeleton made new kinds with no prose, and moving one does not.

**An operation never writes prose of its own.** ``set`` writes the value it
is given. What an operation *can* say about prose it says as a candidate: a
line, carrying no code, about text that may no longer hold where it now
stands. Whether it holds is a question of meaning, which an algorithm does
not decide (K24): the agent judges, the modeller decides.

**A kind is named by its identity, and an identity is not a key.** Wherever
an identity has to resolve to exactly one kind - a subject, a target, the
parent whose children make up a subtree - one that no kind carries, or that
more than one kind carries, refuses the operation rather than picking.
"""

import copy
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "checker"))

import tree  # noqa: E402
from findings import WHITESPACE  # noqa: E402

# The attributes of a kind that are prose and nothing else. The identity is
# absent because nothing edits it; `specialises` because changing it is a
# move; parameters and rules because they are structured, not a string.
PROSE_ATTRIBUTES = (
    "name",
    "text",
    "whenItApplies",
    "howItWouldBeVerified",
    "wordingRule",
)

_NOT_PROSE = {
    "id": (
        "An identity is never edited: every specialises naming this kind "
        "points at it, and it is a label, not something the kind says."
    ),
    "specialises": "Where a kind hangs is changed by move, not by set.",
    "parameters": "Parameters are structured; set edits prose attributes only.",
    "rules": "Rules are structured; set edits prose attributes only.",
}


class Refused(Exception):
    """The operation would have to guess, so it did nothing."""


@dataclass
class Result:
    """What an operation did.

    ``notes`` are facts about structure the operation knows and the checker
    will also report. ``candidates`` are prose that may no longer hold, for
    the agent to judge. The two are kept apart because only the first is
    measured.
    """

    document: dict
    summary: str
    changed: bool = True
    notes: list = field(default_factory=list)
    candidates: list = field(default_factory=list)
    created: str | None = None


# -- finding kinds ------------------------------------------------------------


def _resolve(kinds, identity, role="subject"):
    carrying = tree.positions_carrying(kinds, identity)
    if not carrying:
        raise Refused(f"No kind carries the identity {identity!r}, given as {role}.")
    if len(carrying) > 1:
        raise Refused(
            f"The identity {identity!r}, given as {role}, is carried by "
            f"{len(carrying)} kinds, at positions {carrying}. An identity is "
            f"not a key, so which one is meant is not decided; this is "
            f"reported as duplicate-kind-id."
        )
    return carrying[0]


def _subtree(kinds, root):
    """The positions of ``root`` and every kind beneath it, in order."""
    if root in tree.cyclic_positions(kinds):
        raise Refused(
            f"The kind {kinds[root]['id']!r} sits on a specialisation cycle, so "
            f"it has no subtree; this is reported as specialisation-cycle."
        )
    members = []
    frontier = [root]
    while frontier:
        position = frontier.pop()
        members.append(position)
        identity = kinds[position]["id"]
        carrying = tree.positions_carrying(kinds, identity)
        if len(carrying) > 1:
            raise Refused(
                f"The identity {identity!r}, inside the subtree, is carried by "
                f"{len(carrying)} kinds, at positions {carrying}, so whose "
                f"children the kinds naming it are is not decided; this is "
                f"reported as duplicate-kind-id."
            )
        frontier.extend(
            other
            for other, kind in enumerate(kinds)
            if other != position and kind["specialises"] == identity
        )
    return sorted(members)


def _ancestors(kinds, position):
    """The ancestor chain of ``position``, root first, and a sentence saying
    where it stops short of the root level - or ``None`` when it does not."""
    chain = []
    seen = {position}
    current = position
    while True:
        named = kinds[current]["specialises"]
        if named is None:
            return list(reversed(chain)), None
        carrying = tree.positions_carrying(kinds, named)
        if not carrying:
            return list(reversed(chain)), (
                f"{kinds[current]['id']!r} names {named!r}, which no kind "
                f"carries; this is reported as unknown-parent"
            )
        if len(carrying) > 1:
            return list(reversed(chain)), (
                f"{kinds[current]['id']!r} names {named!r}, which "
                f"{len(carrying)} kinds carry, so neither is taken as its "
                f"parent; this is reported as duplicate-kind-id"
            )
        if carrying[0] in seen:
            return list(reversed(chain)), (
                f"{kinds[current]['id']!r} names {named!r}, which leads back "
                f"into the chain; this is reported as specialisation-cycle"
            )
        current = carrying[0]
        seen.add(current)
        chain.append(current)


# -- prose --------------------------------------------------------------------


def _blank(text):
    return not text.strip(WHITESPACE)


def _label(kind):
    return kind["id"] if _blank(kind["name"]) else kind["name"]


def _chain(kinds, positions):
    return " > ".join(_label(kinds[p]) for p in positions) or "the root level"


def _prose(kind):
    """Every piece of prose a kind carries, with where it is."""
    for attribute in PROSE_ATTRIBUTES:
        yield attribute, kind[attribute]
    for index, parameter in enumerate(kind["parameters"]):
        yield f"parameters[{index}].name", parameter["name"]
        yield f"parameters[{index}].whatToAsk", parameter["whatToAsk"]
    for index, rule in enumerate(kind["rules"]):
        yield f"rules[{index}].whenItApplies", rule["whenItApplies"]
        yield f"rules[{index}].whatToLookFor", rule["whatToLookFor"]


def _mentions(text, name):
    """Whether ``text`` mentions ``name``: at the start of a word, in any
    case. Only the start is anchored, so an inflected or compounded use -
    "radiator's", "Heatingless" - is still found. A candidate that is noise
    costs the agent a glance; one that is missed costs a stale requirement.
    """
    name = name.strip(WHITESPACE)
    if not name:
        return False
    return re.search(r"(?<!\w)" + re.escape(name), text, re.IGNORECASE) is not None


def _mention_candidates(kinds, positions, names, reason, skip=()):
    found = []
    for position in positions:
        kind = kinds[position]
        for where, text in _prose(kind):
            if (position, where) in skip:
                continue
            for name in names:
                if _mentions(text, name):
                    found.append(
                        f"kind {kind['id']!r} ({_label(kind)}), {where}: "
                        f"mentions {name.strip(WHITESPACE)!r}, {reason}."
                    )
    return found


def _names(kinds, positions):
    return [kinds[p]["name"] for p in positions if not _blank(kinds[p]["name"])]


# -- the operations -----------------------------------------------------------


def move(document, subject, target):
    """Cut the subtree under ``subject`` and paste it under ``target``, or at
    the root level when ``target`` is ``None``."""
    document = copy.deepcopy(document)
    kinds = document["kinds"]
    root = _resolve(kinds, subject)
    members = _subtree(kinds, root)
    parent = None
    where = "the root level"
    if target is not None:
        destination = _resolve(kinds, target, "target")
        if destination in members:
            raise Refused(
                f"The target {target!r} lies inside the subtree being moved, so "
                f"once it is cut there is nothing there to paste it under."
            )
        parent = kinds[destination]["id"]
        where = f"{parent!r} ({_label(kinds[destination])})"

    if kinds[root]["specialises"] == parent:
        return Result(
            document, f"{subject!r} already hangs under {where}.", changed=False
        )

    before, _ = _ancestors(kinds, root)
    kinds[root]["specialises"] = parent
    after, _ = _ancestors(kinds, root)

    count = len(members)
    lost = [p for p in before if p not in after]
    candidates = [
        f"The subtree under {subject!r} ({_label(kinds[root])}), {count} "
        f"kind{'s' if count != 1 else ''}, arrived with its prose unchanged. "
        f"Ancestors before: {_chain(kinds, before)}; now: {_chain(kinds, after)}. "
        f"Does what it says still hold beneath its new ancestors?"
    ]
    candidates += _mention_candidates(
        kinds, members, _names(kinds, lost), "an ancestor it no longer has"
    )
    return Result(
        document,
        f"Moved {subject!r} and the {count - 1} kind(s) beneath it under {where}.",
        candidates=candidates,
    )


def delete(document, subject):
    """Delete ``subject`` and every kind beneath it."""
    document = copy.deepcopy(document)
    kinds = document["kinds"]
    root = _resolve(kinds, subject)
    members = set(_subtree(kinds, root))
    gone = {kinds[p]["id"] for p in members}
    gone_names = _names(kinds, sorted(members))

    kept = [kind for position, kind in enumerate(kinds) if position not in members]
    document["kinds"] = kept

    notes = [
        f"kind {kind['id']!r}, rule {rule['id']!r}, implies {rule['implies']!r}, "
        f"which is deleted. The rule is kept and will be reported as "
        f"unknown-implied-definition."
        for kind in kept
        for rule in kind["rules"]
        if rule["implies"] in gone
    ]
    candidates = _mention_candidates(
        kept, range(len(kept)), gone_names, "a kind this deleted"
    )
    return Result(
        document,
        f"Deleted {subject!r} and the {len(members) - 1} kind(s) beneath it.",
        notes=notes,
        candidates=candidates,
    )


def set_attribute(document, subject, attribute, value):
    """Set one prose attribute of ``subject`` to ``value``, as given."""
    if attribute in _NOT_PROSE:
        raise Refused(_NOT_PROSE[attribute])
    if attribute not in PROSE_ATTRIBUTES:
        raise Refused(
            f"A kind has no attribute {attribute!r}. Set edits one of: "
            f"{', '.join(PROSE_ATTRIBUTES)}."
        )
    document = copy.deepcopy(document)
    kinds = document["kinds"]
    position = _resolve(kinds, subject)
    old = kinds[position][attribute]
    if old == value:
        return Result(
            document, f"{attribute} of {subject!r} already holds that.", changed=False
        )
    kinds[position][attribute] = value

    candidates = []
    if attribute == "name" and not _blank(old):
        candidates = _mention_candidates(
            kinds,
            range(len(kinds)),
            [old],
            "the name that kind no longer has",
            skip={(position, "name")},
        )
    return Result(
        document, f"Set {attribute} of {subject!r}.", candidates=candidates
    )


def create(document, parent, name, new_id=None):
    """A new kind under ``parent``, or at the root level when ``parent`` is
    ``None``, carrying a generated identity, ``name``, and nothing else."""
    document = copy.deepcopy(document)
    kinds = document["kinds"]
    where = "the root level"
    if parent is not None:
        position = _resolve(kinds, parent, "parent")
        where = f"{parent!r} ({_label(kinds[position])})"
    identity = new_id or str(uuid.uuid4())
    kinds.append(
        {
            "id": identity,
            "name": name,
            "text": "",
            "whenItApplies": "",
            "parameters": [],
            "rules": [],
            "howItWouldBeVerified": "",
            "wordingRule": "",
            "specialises": parent,
        }
    )
    return Result(
        document, f"Created {identity} under {where}.", created=identity
    )


def extract(document, subject):
    """A standalone package: the subtree under ``subject``, its ancestor
    chain, and the value domains their parameters use."""
    kinds = document["kinds"]
    root = _resolve(kinds, subject)
    members = _subtree(kinds, root)
    chain, stop = _ancestors(kinds, root)
    kept = sorted(set(chain) | set(members))

    extracted = [copy.deepcopy(kinds[p]) for p in kept]
    used = {
        parameter["valueDomainId"]
        for kind in extracted
        for parameter in kind["parameters"]
    }
    carried = {kind["id"] for kind in extracted}

    notes = []
    if stop is not None:
        notes.append(f"The ancestor chain stops short of the root level: {stop}.")
    notes += [
        f"kind {kind['id']!r}, rule {rule['id']!r}, implies {rule['implies']!r}, "
        f"which the extract leaves out; the extract will report it as "
        f"unknown-implied-definition."
        for kind in extracted
        for rule in kind["rules"]
        if rule["implies"] is not None and rule["implies"] not in carried
    ]
    result = {
        "schemaVersion": document["schemaVersion"],
        "name": document["name"],
        "version": document["version"],
        "valueDomains": [
            copy.deepcopy(d) for d in document["valueDomains"] if d["id"] in used
        ],
        "kinds": extracted,
    }
    return Result(
        result,
        f"Extracted {subject!r}: {len(chain)} ancestor(s) and "
        f"{len(members)} kind(s) in its subtree.",
        notes=notes,
    )
