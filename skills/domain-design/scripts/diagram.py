"""One kind's neighbourhood, as a Mermaid class diagram.

    python skills/domain-design/scripts/diagram.py path/to/package.yaml <identity>

One subject, one diagram. There is no whole-package mode and no fallback:
assembling more than one picture is the agent's business, and a diagram of
nothing helps nobody.

What the tree *is* - which kind a ``specialises`` names, what falls out for
sitting on a cycle - is not decided here. ``tree`` decides it, for the
checker and for this alike.

**stdout is always a Mermaid diagram, never a diagram plus something else.**
Anything the command has to say about what it drew - a parent left out, an
identity two drawn kinds share - is a trailing ``%%`` line: a Mermaid
comment, inside the same fence as the diagram it explains. The fence stays
valid wherever it is pasted, and an agent reading stdout still sees the
sentence and can relay it to the modeller.

The exit status says what kind of answer this is:

    0   a diagram was written for the subject - gaps or not
    1   the subject given will not be drawn
    2   there is nothing to draw from at all
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
    # Flattened on the line boundaries `str.splitlines()` knows, not on
    # `WHITESPACE`. The two sets answer different questions and must stay
    # different: `WHITESPACE` is the contract's own, narrower notion of
    # blank text, which deliberately leaves U+0085 and its relatives out -
    # a name made of one of them is a name, not blank. Here the question is
    # which characters the *output* reads as ending a line, and that is a
    # wider set with nothing to do with blankness; `str.splitlines()` names
    # it exactly, because it is what will read this text back.
    single_line = " ".join(name.splitlines())
    return _RUNS.sub(" ", single_line).strip(WHITESPACE).replace('"', "#quot;")


def _label_of(kinds, position):
    """What a kind's box says: its name. Every box carries one, because the
    class name underneath is the kind's identity, a UUID that says nothing to
    a reader.

    Until names are required and unique, a name that is unwritten, or that
    another kind in the package carries too, has the first six characters of
    the identity added, so two such boxes can still be told apart. The editor
    labels the same box the same way.
    """
    kind = kinds[position]
    name = kind["name"].strip(WHITESPACE)
    shared = name and any(
        other != position and kinds[other]["name"].strip(WHITESPACE) == name
        for other in range(len(kinds))
    )
    if name and not shared:
        return name
    return f"{name or '(unnamed)'} · {kind['id'][:6]}"


def _duplicate_identity_comments(kinds, positions, names):
    """One ``%%`` comment for each identity that more than one drawn kind
    carries.

    Two kinds may truly specialise one identity — a child is not a
    reference that has to resolve to exactly one kind, it is a kind that
    points *at* the subject — so both are drawn. But the Mermaid class
    name is what tells their boxes apart, and that name is not in the
    package, so a reader cannot: this says so.
    """
    # No "subject" or "parent" filter here: each already has exactly one
    # carrier by the time this runs, or `tree.neighbourhood` has refused to
    # draw at all - see the analogous note in `tree.py` for children. Only
    # two or more children can still share an identity here.
    by_identity = {}
    for position in positions:
        by_identity.setdefault(kinds[position]["id"], []).append(position)
    return [
        f"%% The identity {identity!r} is carried by {len(shared)} of the "
        f"drawn kinds; nothing in the package tells their boxes apart — "
        f"reported as duplicate-kind-id."
        for identity, shared in by_identity.items()
        if len(shared) > 1
    ]


def to_mermaid(kinds, near):
    """``near``, drawn. Every edge in the result is one the package states.

    Anything the diagram cannot say as a box or an edge is appended as
    trailing ``%%`` comment lines — see the module docstring.
    """
    positions = sorted(
        {near.subject, *near.children}
        | ({near.parent} if near.parent is not None else set())
    )
    names = _assign_names(kinds, positions)

    body = []
    uses_root = False
    for position in positions:
        own = names[position]
        body.append(f'\tclass {own}["{_label(_label_of(kinds, position))}"]')

        if position == near.subject:
            if near.parent is not None:
                body.append(f"\t{names[near.parent]} <|-- {own}")
            elif kinds[near.subject]["specialises"] is None:
                # A positive test, derived from the package: a root kind's
                # parent really is the abstract root, so that edge is
                # true. Not the else of a chain over near's flags — a
                # fourth state there would otherwise fall into this
                # branch, the one that claims "this is a root kind".
                uses_root = True
                body.append(f"\t{ROOT} <|-- {own}")
            # Neither a parent no kind carries nor one that sits on a
            # cycle gets an edge: an edge up to the abstract root would
            # call the subject a root kind when it is not. The two are
            # told apart in words, not in the diagram — see below.
        elif position in near.children:
            body.append(f"\t{names[near.subject]} <|-- {own}")

    lines = ["classDiagram"]
    if uses_root:
        lines += [f"\tclass {ROOT} {{", "\t\t<<abstract>>", "\t}"]
    lines += body
    lines.append(f"\tstyle {names[near.subject]} {_MARK}")

    lines += _duplicate_identity_comments(kinds, positions, names)
    if near.parent_cyclic is not None:
        parent_identity = kinds[near.parent_cyclic]["id"]
        lines.append(
            f"%% The parent it names, {parent_identity!r}, sits on a "
            f"specialisation cycle and so is not drawn — reported as "
            f"specialisation-cycle."
        )
    elif near.parent_missing:
        parent_identity = kinds[near.subject]["specialises"]
        lines.append(
            f"%% The parent it names, {parent_identity!r}, is carried by "
            f"no kind and so is not drawn — reported as unknown-parent."
        )
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
