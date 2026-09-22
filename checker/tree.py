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
