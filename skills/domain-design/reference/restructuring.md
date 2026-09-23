# Restructuring a domain

What a change to an existing tree of kinds can be, and what each does to the prose already written. Read it
before planning any change that moves, merges, splits or removes existing kinds.

Every restructuring below is a composition of the five operations -- `create`, `move`, `delete`, `set`,
and `extract` for reading -- so none needs a tool of its own. What differs between them is what they do to
**prose**, and that is what this file is for. Where the operations' own candidates already say everything
worth saying, a restructuring has no recipe; where they cannot, because the question is one of meaning, it
has one.

Values are not inherited down the tree: what specialisation licenses a child to add, narrow or override is
ProjectML's OQ9, and it is open (see `specialisation-and-domains.md`). So no recipe ever deletes a child's
statement because its parent now says the same. It says that the two overlap, and leaves it there.

## The catalogue

In inverse pairs: a restructuring whose inverse is missing is a hint that something is. The examples are
invented.

| # | Restructuring | Inverse | Made of | Recipe |
|---|---|---|---|---|
| 1 | **Grouping** related siblings under a new common parent -- *boilers and heat pumps under "heat source"* | 2 | create, moves | Grouping |
| 2 | **Removing a level**: an intermediate kind goes, its children rise to its parent | 1 | moves, delete | -- |
| 3 | **Widening**: a more general parent over a root or a branch -- *"heating" beneath a new "building services"* | 4 | create, move | Grouping |
| 4 | **Narrowing**: a too-general root goes, its children become roots | 3 | moves, delete | -- |
| 5 | **Reparenting** a misclassified branch | itself | move | -- |
| 6 | **Promotion**: a branch becomes a sibling of its parent, not a specialisation of it | 7 | move | -- |
| 7 | **Demotion**: a kind becomes a specialisation of its sibling | 6 | move | -- |
| 8 | **Splitting into specialisations**: a kind becomes a parent, its content distributed among new children | 9 | creates, sets | Splitting |
| 9 | **Folding a specialisation back**: a child that adds nothing merges into its parent | 8 | moves, set, delete | Merging |
| 10 | **Splitting into peers**: one kind becomes two siblings, and the original goes | 11 | creates, sets, delete | Splitting |
| 11 | **Merging** two siblings that ask the same question | 10 | moves, set, delete | Merging |
| 12 | **Regrouping** kinds from different branches under a new parent | -- | create, moves | Regrouping |
| 13 | **Re-cutting a level** by another criterion -- *by fuel* to *by function* | itself | 2s and 12s | its parts' |
| 14 | **Lifting** what siblings share into their parent | 15 | sets | Grouping |
| 15 | **Pushing down** a parent's statement true of only some children | 14 | sets | Splitting |

Two pairs look alike and are not:

- **2 and 9** are the same change to the tree -- a node goes, its children rise -- with opposite prose. In
  2 the children's text survives and the removed level's is dropped; in 9 the parent absorbs the child's.
- **1 and 12** differ only in where the kinds come from, and that decides the prose. Siblings grouped in 1
  already share a parent, so what they share can be read off them. Kinds gathered from different branches
  in 12 share nothing written yet.

A restructuring with no recipe is covered by the operations' candidates: every kind a move puts under new
ancestors is reported, with the ancestor it lost, and the mentions of a deleted kind are found.

## Grouping

For 1, 3 and 14. *Proven on a real reorganisation.*

1. `create` the new parent under the siblings' parent, or at the root level.
2. `move` each sibling under it.
3. Read the siblings together. Propose, as the new parent's prose, what they **all** say -- only that.
4. Where a sibling says what its new parent now says, report the overlap as an opinion. Do not propose
   deleting it: whether it still needs saying is OQ9's question, not yours.

**Widening is grouping over a single kind.** When a domain turns out wider than it was drawn -- or a
proposed rename would make a kind mean more than it did -- the kind is not renamed wider. A new, more
general parent goes above it, and the kind keeps its subject and its prose. The opinion to raise when a
rename looks like this: *this would make the kind mean more than it did -- does its old subject still hold?
If so, it stays, beneath a wider parent.* A rename that stretches a kind invalidates every sentence written
about its old subject, and the checker sees none of it.

## Regrouping

For 12. *Not yet exercised on a real case.*

1. `create` the new parent where it belongs.
2. `move` each kind under it, from wherever it is.
3. Each moved kind lost different ancestors; judge each move's candidates on its own.
4. What the gathered kinds share is written nowhere. The new parent's prose is **new content**: ask the
   modeller what makes them one group, rather than assembling it from their texts. *What do these have in
   common that made you put them together?*

## Splitting

For 8, 10 and 15. *Not yet exercised on a real case.*

1. `create` the new kinds -- as children of the original (8), or beside it (10).
2. Distribute the original's prose among them with `set`, each statement placed **once**.
3. For 10, `delete` the original once nothing points at it.
4. Check the distribution for a statement that went nowhere and one that went to two places, and report
   either as an opinion. For 8, also: is what stays on the parent now true of **every** child? If a
   statement is true of only some, it belongs on them (15).

## Merging

For 11 and 9. *Not yet exercised on a real case.*

1. Read the two texts side by side and look for where they **contradict**. Raise each contradiction as an
   opinion: *which of these holds -- or are these two kinds after all?* A contradiction the modeller cannot
   settle is evidence against the merge; stop and say so.
2. Decide which kind survives; the other is absorbed.
3. `move` the absorbed kind's children under the survivor.
4. Write the survivor's prose with `set`, from both texts.
5. `delete` the absorbed kind.

The first real case that runs into an unproven recipe proves it or corrects it.
