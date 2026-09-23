"""What the specialisation tree of a package is.

One statement of it on this side, because two are how two readings of one
package begin to differ. The checker reports on the tree and the skill's
diagram script draws it, and both read this.

A `specialises` names an identity, not a kind, and an identity is free text
the modeller edits: two kinds may carry one, and a kind may carry none. So an
edge here goes to *every* position carrying the identity named, and a caller
that needs exactly one — a drawing does — asks and is told when there is not
exactly one.
"""

from dataclasses import dataclass


def specialisation_edges(kinds):
    """For each kind, by its position in ``kinds``, the positions of the
    kinds that carry the identity it specialises."""
    positions = {}
    for position, kind in enumerate(kinds):
        positions.setdefault(kind["id"], []).append(position)
    return [
        [] if kind["specialises"] is None else positions.get(kind["specialises"], [])
        for kind in kinds
    ]


def on_a_cycle(edges, start):
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


def positions_carrying(kinds, identity):
    """The positions of the kinds carrying ``identity``, in declaration
    order. Empty when no kind carries it, and longer than one when more than
    one does — both ordinary states the checker reports rather than prevents."""
    return [
        position for position, kind in enumerate(kinds) if kind["id"] == identity
    ]


def cyclic_positions(kinds):
    """The positions of the kinds sitting on a specialisation cycle.

    A kind that only descends from one is not on it.
    """
    edges = specialisation_edges(kinds)
    return {
        position for position in range(len(kinds)) if on_a_cycle(edges, position)
    }


class NotDrawable(Exception):
    """The subject has no neighbourhood that could be drawn truthfully."""


@dataclass(frozen=True)
class Neighbourhood:
    """One hop around a subject, in positions.

    The parent is in exactly one of three states, told apart by ``parent``,
    ``parent_missing`` and ``parent_cyclic`` together. ``parent`` gives a
    position when there is a kind to draw an edge to. ``parent_missing`` is
    true when no kind carries the identity named at all — an edge to the
    abstract root would call that a root kind, which it is not.
    ``parent_cyclic`` gives the position of the parent when a kind *does*
    carry the named identity but sits on a specialisation cycle: carried, but
    not drawn, because a kind on a cycle has no place in a tree — a caller
    that draws the subject still owes the modeller a word about why that
    parent is absent, which ``parent_missing`` alone would say wrongly. All
    three are ``None``/``False`` only for a root kind, whose parent really is
    the abstract root.
    """

    subject: int
    parent: int | None
    parent_missing: bool
    parent_cyclic: int | None
    children: tuple[int, ...]


def neighbourhood(kinds, subject):
    """The subject, its direct parent and its direct children, by position.

    ``subject`` is a position rather than an identity, because an identity is
    not a key. Raises ``NotDrawable`` where drawing would have to guess.

    Ambiguity is counted over every kind carrying an identity, cyclic or not:
    a shared identity is invalid on its own terms, independent of where its
    carriers sit. Only once an identity is known to have exactly one carrier
    does whether that carrier sits on a cycle come into it.
    """
    cyclic = cyclic_positions(kinds)
    if subject in cyclic:
        raise NotDrawable(
            "the kind sits on a specialisation cycle, so it has no place in "
            "a tree, reported as specialisation-cycle"
        )

    identity = kinds[subject]["id"]
    sharing = positions_carrying(kinds, identity)
    if len(sharing) > 1:
        raise NotDrawable(
            f"the identity {identity!r} is carried by {len(sharing)} kinds, at "
            f"positions {sharing}, so whose children these are is not decided"
        )

    parent = None
    parent_missing = False
    parent_cyclic = None
    named = kinds[subject]["specialises"]
    if named is not None:
        carriers = positions_carrying(kinds, named)
        if len(carriers) > 1:
            raise NotDrawable(
                f"the parent identity {named!r} is carried by {len(carriers)} "
                f"kinds, at positions {carriers}, so which is the parent is not "
                f"decided"
            )
        if not carriers:
            parent_missing = True
        elif carriers[0] in cyclic:
            parent_cyclic = carriers[0]
        else:
            parent = carriers[0]

    # No "not in cyclic" filter here: a child's only edge is to `subject`
    # (the sole carrier of `identity`, established above), so a cyclic
    # child would have to reach back to itself through `subject` — which
    # would make `subject` cyclic too, and that is already refused above.
    children = tuple(
        position
        for position in range(len(kinds))
        if position != subject and kinds[position]["specialises"] == identity
    )
    return Neighbourhood(subject, parent, parent_missing, parent_cyclic, children)
