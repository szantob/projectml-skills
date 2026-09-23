# What specialising means, and what a value domain is

Read this before drawing, proposing, or judging the edge between two kinds, or the domain a parameter draws
from. It says what the edge and the domain *are* — what a reader is deciding when they place one — not what
shape either takes on the page. This file is read independently of the one on a definition's eight
attributes: it does not build on that file, and does not repeat it.

## Every definition is a specialisation

No element in a model is a `RequirementDefinition` and nothing more: a definition exists only as a
specialisation of it (K30). `RequirementDefinition` itself is abstract — it describes what every kind has in
common, not a kind a project could produce a requirement under. Declaring a kind is declaring a
specialisation of it, never filling in an attribute that names one.

Which specialisations exist — how many, what they are called, on what axis they divide — is an
implementation's business, not the metamodel's. The metamodel fixes the mechanism and says nothing about the
tree an implementation grows with it.

## `specialises` names an identity, not a kind

A kind does not point at another kind directly. It names the identity that other kind carries, and identity
is a free-text attribute a person edits — the same status a definition's own identity has. Naming an
identity is therefore not the same thing as naming a kind: the reference can fail to resolve, if nothing
carries the identity named, and it can resolve to more than one thing, if two kinds carry the same identity.

Both are possible because nothing about `specialises` makes them impossible, and neither is silently
allowed. A model where two definitions carry one identity is invalid on its own terms, independent of
`specialises` — the metamodel states uniqueness of identity as a syntactic constraint, decidable without
reading what either definition says (K24) — and a `specialises` that names a shared identity inherits that
invalidity rather than picking a winner. This is why a checker reports an unresolved or an ambiguous
`specialises` instead of guessing which kind was meant, and why a tree diagram declines to draw a subject
whose identity more than one kind carries: there is no fact of the matter for it to draw.

## Specialising does not inherit values

A kind that specialises another does not thereby receive its ancestor's attribute values. Showing a
descendant's parameters, its wording, its verification method beside the ancestor's own is useful — a reader
comparing the two is exactly how a specialisation earns its place — but showing is not copying, and nothing
here treats an ancestor's value as a default a descendant starts from.

**What specialisation actually licenses a subtype to add, narrow, or override is open — ProjectML's OQ9, and
it is unresolved.** K30 chose the mechanism, specialisation, without defining what exercising it means. A
tool that copied an ancestor's value down the tree would be answering OQ9 by accident, in code, for every
package it touched — settling by convenience a question the metamodel has deliberately left for whoever
first has a real tree to reason from. Until then, an ancestor's value is shown for comparison and never
copied.

## A value domain is what a parameter draws from

Every parameter a definition declares names the value domain it draws from — the range of things a value for
that parameter could be. As with the set of kinds, which value domains exist, and what they are called, is
an implementation's business rather than the metamodel's: the metamodel provides the slot a domain fills
without naming what goes into it (K30).

**Whether a domain fixes a unit is open — ProjectML's OQ27, and it is unresolved.** Two values in the same
domain are already presumed comparable elsewhere in the metamodel — a conflict between them is meaningless
otherwise — but nothing settles whether that comparability comes from the domain fixing one unit, so that a
value need carry none of its own, or from the domain leaving units alone, so that a value must carry one to
be comparable at all. Treating a domain as though it obviously fixed a unit, or obviously did not, is
answering OQ27 in passing, and a convenience reached that way is exactly the failure this file exists to
head off. Declare a domain; do not decide, on its behalf, a question the metamodel has not decided.

## What good shape looks like in a tree

**The rest of this file states what the metamodel and its open questions require. This last part does not —
it is guidance, not a rule traced to any decision, and it can be wrong in a way a citation cannot.**

A specialisation earns its place by narrowing what its parent already asks — sharpening a parameter, tightening
what to ask for it, restating a verification method for a more specific case — not merely by adding something
beside it. A kind that only adds is not yet using the edge for anything the parent could not have carried
itself.

A tree that is wide at every level, with little narrowing from one level to the next, is usually a list
wearing a tree's clothes: the specialisations are really just alternatives, related by nothing more than
sharing a parent, and the edge between them and it is doing no work. A tree earns the name when descending it
means the definitions get more specific, not merely more numerous.
