# What a `RequirementDefinition` is

Read this before writing or judging any one of a `RequirementDefinition`'s eight attributes: it says what
each one *means* — what a reader is deciding when they write it — not what shape it takes on the page. The
package's own written shape, and the checks run over that shape, belong to the contract, not to this file.

## A definition is not a requirement

A `RequirementDefinition` is not a requirement. It is the definition of a *kind* of requirement — what a
whole family of requirements will have in common — and a requirement is produced under one, the way an
instance is produced under its class. Writing a definition is domain work done once, for every requirement
that will ever be produced under it; filling in one requirement's own values happens later, and elsewhere.

ProjectML separates the two by level. There are three: a metamodel says what a `RequirementDefinition` is,
an implementation is a filled set of definitions together with the notation and rule-set that go with them,
and a project model is what a team builds with that implementation — an implementation is, in turn, a
metamodel for the project models built beneath it (K16). A definition belongs to the middle level, a
domain's own level; the requirements a project model instantiates from it belong to the level below.
Treating a definition as though it already carried one requirement's answer — a value settled rather than a
shape waiting to be filled — mistakes the middle level for the bottom one.

## The eight attributes

`RequirementDefinition` carries eight attributes, and they are the whole of what the metamodel can read
without depending on anything an implementation supplies (K27). Each earns its place because there is a
question about it a reader must answer — not because it has a particular shape, which is the contract's
business.

- **Identity.** The definition's identifier — what tells this definition apart from every other one when
  something has to name it. Deciding an identity is choosing a label, not summarising what the definition
  says; a bad identity is one that tries to also carry the definition's name or its wording.

- **Name.** The human-readable label a person reads. Deciding a name is deciding what someone scanning a
  list of definitions would look for; nothing else here depends on it.

- **The wording template.** The structural pattern a requirement's wording is produced from, with places
  left for the definition's parameters. Writing this is deciding the sentence shape every requirement of
  this kind will share — not what any one requirement will say, which depends on the parameter values a
  particular requirement fills in later.

- **When it applies.** One sentence stating the circumstance under which this definition comes into play.
  It carries a claim of its own that is easy to get backwards — see below.

- **Parameters.** The variables a requirement of this kind fills in, each one naming the value domain it
  draws from. Declaring a parameter is deciding what varies from one requirement of this kind to the next;
  which value domains exist for it to draw from is an implementation's business, exactly as which kinds
  exist is (K30).

- **What to ask.** For each parameter, how a non-expert is asked for the value that is missing. It is
  written once per parameter, not once per definition — see below for why.

- **How it would be verified.** The method by which a requirement produced under this definition would be
  shown to hold, written once for the kind rather than once per requirement. It sits on the definition
  rather than on the requirement because a verification method is generic to a kind — a property of what
  sort of thing is being checked, not of the one instance in front of a reviewer — so a requirement produced
  under a definition that carries this inherits it without needing one of its own (K29).

- **The wording rule.** A well-formedness rule for the wording a requirement produced under this definition
  must satisfy. It stands on the same footing as *how it would be verified* — see below.

A bad attribute, on any of the eight, is one answering a different question than the one it was asked: a
name doing the work of an identity, a wording template trying to say when the definition applies, an
identity trying to describe what the definition is for. The eight stay separate because each is a separate
decision, and folding two into one field loses the record of which decision was actually made.

## Two attributes answer to the value-state model, not to a design language

*Parameters* and *what to ask* do not take their meaning from any notation or design language. A parameter
with no value yet is not a special case — it is a value in the unknown state, the same state any value can
be in before it is filled in. *What to ask* is how that value is obtained from somebody who holds it: the
question that turns an unknown value into a known one.

This is also why *what to ask* is written per parameter and not once per definition. Each parameter can be
missing on its own, independently of the others, so each needs its own question — one *what to ask* per
unknown, not a single question trying to cover every unknown a definition might ever have at once.

## When it applies is prose, and its absence is a gap, not a claim

*When it applies* is one sentence of prose, not an expression a program evaluates (D20). Writing it is
stating, in words, the circumstance that brings this definition into play — not encoding a condition for
something else to check against a requirement's values.

Because it is prose, an unwritten *when it applies* means exactly that: nobody has written down when this
definition applies yet. It does not mean the definition applies unconditionally, and reading it that way
gets the absence backwards — a gap still waiting to be filled is not the same thing as a decision that the
definition always fires.

## The wording rule stands where how it would be verified stands

The wording rule is prose, on the same terms as *how it would be verified* (K66): a well-formedness rule for
a requirement's wording, stated once for the kind, read rather than evaluated. The wording template already
gives the structural pattern a requirement's wording is produced from; the wording rule says something the
template alone cannot — the qualities that wording must have once it exists, not the shape it is assembled
into. Writing one is deciding what "well-formed," for this kind of requirement, actually means in words —
not building a check that runs.

## Presence, not content — an algorithm does not decide what prose means

Every prose attribute above — *when it applies*, *how it would be verified*, the wording rule — is checked
for being there, never for what it says (K24). An algorithm does not decide what prose means: judging
whether a sentence actually captures the right condition, the right verification method, or the right
notion of well-formedness is a question about content, and the metamodel leaves questions about content to
whoever is reading, not to a check. What a check can do is notice a gap: a field left empty is something a
rule can fail on, without reading a word of what a filled one would have said.

This is why the skill filling in these attributes may hold an opinion about a piece of prose — that it
reads oddly, that it is broader than it should be, that it says less than it needs to — without that opinion
ever becoming a check the way a missing field is a check. Write a *when it applies*, a verification method,
and a wording rule that are actually believed to be right: nothing downstream catches a sentence that is
present but wrong, only one that is missing.

## What this does not cover

This covers a definition's own eight attributes — phase 1. A `Rule`, and how one relates to a definition, is
phase 2, and is out of scope here.
