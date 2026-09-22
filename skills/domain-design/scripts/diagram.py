"""One kind's neighbourhood, as a Mermaid class diagram.

One subject, one diagram. There is no whole-package mode and no fallback:
assembling more than one picture is the agent's business, and a diagram of
nothing helps nobody.

What the tree *is* - which kind a ``specialises`` names, what falls out for
sitting on a cycle - is not decided here. ``tree`` decides it, for the
checker and for this alike.
"""

import re
import sys
from pathlib import Path

# Run as a script, this file's own directory is the only thing on the path,
# and the checker it reads the tree from is four levels up. Tests reach it
# through their conftest; a modeller running the command reaches it here.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "checker"))

from findings import WHITESPACE  # noqa: E402

ROOT = "RequirementDefinition"

_UNSAFE = re.compile(r"[^A-Za-z0-9_]")
_RUNS = re.compile("[" + WHITESPACE + "]+")

# The subject's mark. A `style` statement, not `classDef` plus `cssClass`:
# in a class diagram the latter pair renders nothing. A fill alone would not
# survive greyscale, so the mark carries a heavier border too.
_MARK = "fill:#fff3bf,stroke:#a06800,stroke-width:3px"


def _sanitise(identity):
    """Mermaid accepts only ``A-Za-z0-9_``, and no leading digit."""
    cleaned = _UNSAFE.sub("_", identity) or "_"
    return "_" + cleaned if cleaned[0].isdigit() else cleaned


def _assign_names(kinds, positions):
    """A distinct, valid Mermaid class name for each drawn kind.

    Keyed by position, not by identity: two kinds may carry one identity, and
    each still needs a box of its own. ``ROOT`` is reserved for the diagram's
    own abstract root and is never handed to a kind.
    """
    taken = {ROOT}
    names = {}
    for position in positions:
        base = _sanitise(kinds[position]["id"])
        candidate = base
        suffix = 1
        while candidate in taken:
            candidate = f"{base}_{suffix}"
            suffix += 1
        taken.add(candidate)
        names[position] = candidate
    return names


def _label(name):
    """A name, flattened onto one line with its quotes made safe.

    A name is free text, and an unescaped quote or line break ends the label
    early and breaks the whole diagram rather than the one box.
    """
    return _RUNS.sub(" ", name).strip(WHITESPACE).replace('"', "#quot;")


def to_mermaid(kinds, near):
    """``near``, drawn. Every edge in the result is one the package states."""
    positions = sorted(
        {near.subject, *near.children}
        | ({near.parent} if near.parent is not None else set())
    )
    names = _assign_names(kinds, positions)

    body = []
    uses_root = False
    for position in positions:
        own = names[position]
        name = _label(kinds[position]["name"])
        if name:
            body.append(f'\tclass {own}["{name}"]')

        if position == near.subject:
            if near.parent is not None:
                body.append(f"\t{names[near.parent]} <|-- {own}")
            elif not near.parent_missing:
                # A root kind's parent really is the abstract root, so that
                # edge is true. A subject naming a parent no kind carries
                # gets no edge at all: silence says there is something wrong
                # above, where an edge would say it is a root kind.
                uses_root = True
                body.append(f"\t{ROOT} <|-- {own}")
        elif position in near.children:
            body.append(f"\t{names[near.subject]} <|-- {own}")

    lines = ["classDiagram"]
    if uses_root:
        lines += [f"\tclass {ROOT} {{", "\t\t<<abstract>>", "\t}"]
    lines += body
    lines.append(f"\tstyle {names[near.subject]} {_MARK}")
    return "\n".join(lines)
