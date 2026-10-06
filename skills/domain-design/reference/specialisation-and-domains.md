# What specialising means, and what a value domain is

Read this before drawing, proposing, or judging the edge between two kinds, or the domain a parameter draws
from. It says what the edge and the domain *are* — what a reader is deciding when they place one — not what
shape either takes on the page. This file is read independently of the one on a definition's nine
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

## What specialising inherits: parameters, and nothing else

**A specialisation has every parameter its ancestors declare, in addition to its own** (K107), each with its
*what to ask* (K112). It is the same parameter all the way down — one identity, one value domain, one ask —
so a descendant **never declares a parameter an ancestor already declares** (K108), under that identity or
under that name: a rule stated high in the tree must find the same parameter on every kind it reaches. Where
a parameter belongs to every kind beneath some point, it belongs on that point, declared once.

**Nothing else is inherited.** A definition's wording template is its own: a descendant inherits the
parameters, never the sentence (K113). Its *when it applies* is its own too, because it says which branch of
the tree is worth following and an inherited one would point every branch the same way (K114). Whether a
definition is abstract is not inherited either (K109).

**What is still open is ProjectML's OQ9, narrowed:** whether an inherited parameter may ever be overridden or
narrowed, whether a wording rule is inherited, and whether *how it would be verified* is. A tool that copied
an ancestor's wording rule or verification method down the tree would be answering OQ9 by accident, in code,
for every package it touched. Until it is answered, an ancestor's prose is shown for comparison and never
copied.

## A value domain is what a parameter draws from

Every parameter a definition declares names the value domain it draws from — the range of things a value for
that parameter could be. As with the set of kinds, which value domains exist, and what they are called, is
an implementation's business rather than the metamodel's: the metamodel provides the slot a domain fills
without naming what goes into it (K30).

**A domain fixes no unit; it declares how its values compare** (K101). Exactly one of three: **not
comparable**, **comparable for equality**, or **ordered**, the last including the second. That is what a
rule's guard needs, and nothing more: *equals* and *is one of* need a domain comparable for equality or
ordered, *less than* and its relatives an ordered one. How a domain achieves its level — a fixed unit, an
enumeration, anything else — is the implementation's business. Two domains for one measure in different
units are two ordered domains, each in its own unit, and nothing ever converts between them; a domain is
declared as comparable as its values really are, and no more.

## What good shape looks like in a tree

**The rest of this file states what the metamodel and its open questions require. This last part does not —
it is guidance, not a rule traced to any decision, and it can be wrong in a way a citation cannot.**

A specialisation earns its place by being a narrower case of what its parent describes — a wording template
that says the more specific thing, a *when it applies* that picks out the narrower circumstance, a
verification method fitted to the more specific case — not merely by sitting beside it. It does not earn it
by re-asking for its parent's parameters: those it already has, with their asks. A kind that differs from its
parent in nothing it says is not yet using the edge for anything.

A kind whose only purpose is to hold what its children share — their parameters, a *when it applies* that
guides the choice between them — is a candidate for being abstract. One that is abstract and has no children
holds parameters nothing will ever fill, which is worth an opinion.

A tree that is wide at every level, with little narrowing from one level to the next, is usually a list
wearing a tree's clothes: the specialisations are really just alternatives, related by nothing more than
sharing a parent, and the edge between them and it is doing no work. A tree earns the name when descending it
means the definitions get more specific, not merely more numerous.
