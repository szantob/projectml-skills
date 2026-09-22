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

    ``parent`` is ``None`` both for a root kind and for one naming a parent
    that does not exist; ``parent_missing`` is what tells the two apart, and
    a drawing must, because an edge to the abstract root would call the
    second a root kind when it is not.
    """

    subject: int
    parent: int | None
    parent_missing: bool
    children: tuple[int, ...]


def neighbourhood(kinds, subject):
    """The subject, its direct parent and its direct children, by position.

    ``subject`` is a position rather than an identity, because an identity is
    not a key. Raises ``NotDrawable`` where drawing would have to guess.
    """
    cyclic = cyclic_positions(kinds)
    if subject in cyclic:
        raise NotDrawable(
            "the kind sits on a specialisation cycle, so it has no place in a tree"
        )

    identity = kinds[subject]["id"]
    sharing = [
        position
        for position in positions_carrying(kinds, identity)
        if position not in cyclic
    ]
    if len(sharing) > 1:
        raise NotDrawable(
            f"the identity {identity!r} is carried by {len(sharing)} kinds, at "
            f"positions {sharing}, so whose children these are is not decided"
        )

    parent = None
    parent_missing = False
    named = kinds[subject]["specialises"]
    if named is not None:
        carriers = [
            position
            for position in positions_carrying(kinds, named)
            if position not in cyclic
        ]
        if len(carriers) > 1:
            raise NotDrawable(
                f"the parent identity {named!r} is carried by {len(carriers)} "
                f"kinds, at positions {carriers}, so which is the parent is not "
                f"decided"
            )
        if carriers:
            parent = carriers[0]
        else:
            parent_missing = True

    children = tuple(
        position
        for position in range(len(kinds))
        if position != subject
        and position not in cyclic
        and kinds[position]["specialises"] == identity
    )
    return Neighbourhood(subject, parent, parent_missing, children)
