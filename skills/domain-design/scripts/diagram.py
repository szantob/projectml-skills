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

import contract_schema  # noqa: E402
import dialect  # noqa: E402
import tree  # noqa: E402
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
            elif near.parent_missing or near.parent_cyclic is not None:
                # Neither a parent no kind carries nor one that sits on a
                # cycle gets an edge: an edge up to the abstract root would
                # call the subject a root kind when it is not. The two are
                # told apart in words, not in the diagram — see draw().
                pass
            else:
                # A root kind's parent really is the abstract root, so that
                # edge is true.
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


def _subject_position(kinds, subject):
    """Which kind is meant, or a sentence saying why that is not decided."""
    carrying = tree.positions_carrying(kinds, subject)
    if not carrying:
        return None, f"No kind carries the identity {subject!r}."
    if len(carrying) > 1:
        return None, (
            f"The identity {subject!r} is carried by {len(carrying)} kinds, at "
            f"positions {carrying}. An identity is not a key, and a model "
            f"where more than one definition carries it is not valid; this is "
            f"reported as duplicate-kind-id."
        )
    return carrying[0], None


def draw(text, subject, out):
    """Draw ``subject`` from the package in ``text``, and return the exit
    status."""
    try:
        document = dialect.load(text)
    except dialect.Unreadable as error:
        out.write(f"Cannot be read: {error}\n")
        return 2

    wrong = contract_schema.misfits(document)
    if wrong:
        # The drawer cannot even look for a subject in a package that does
        # not fit the schema, so a misfit joins "nothing to draw from" here,
        # unlike the checker, for which a misfit is as wrong as an issue.
        out.write("Does not fit the schema:\n")
        for line in wrong:
            out.write(f"  - {line}\n")
        return 2

    kinds = document["kinds"]
    where, refusal = _subject_position(kinds, subject)
    if refusal is not None:
        out.write(f"{refusal}\n")
        return 1

    try:
        near = tree.neighbourhood(kinds, where)
    except tree.NotDrawable as error:
        out.write(f"Nothing can be drawn for this subject: {error}.\n")
        return 1

    out.write(to_mermaid(kinds, near) + "\n")
    if near.parent_cyclic is not None:
        parent_identity = kinds[near.parent_cyclic]["id"]
        out.write(
            f"The parent it names, {parent_identity!r}, sits on a "
            f"specialisation cycle and so is not drawn — reported as "
            f"specialisation-cycle.\n"
        )
    return 0


def main(argv):
    # A package may hold any language; a Windows console does not default to
    # one that can print it.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    usage = (
        "Usage: python skills/domain-design/scripts/diagram.py "
        "path/to/package.yaml <identity>"
    )
    if len(argv) != 3:
        print(usage)
        return 2
    subject = argv[2]

    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as error:
        print(f"Cannot be read: {error}")
        return 2
    except UnicodeDecodeError:
        # A file in some other encoding is not a package this can read, and
        # saying so is not the same answer as "this subject will not be
        # drawn": it must not reach the exit status that means that.
        print(f"Cannot be read: {argv[1]} is not UTF-8 text.")
        return 2

    return draw(text, subject, sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
