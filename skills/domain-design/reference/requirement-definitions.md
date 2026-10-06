# What a `RequirementDefinition` is

Read this before writing or judging any one of a `RequirementDefinition`'s nine attributes: it says what
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

## The nine attributes

`RequirementDefinition` carries nine attributes, and they are the whole of what the metamodel can read
without depending on anything an implementation supplies (K27). Each earns its place because there is a
question about it a reader must answer — not because it has a particular shape, which is the contract's
business.

- **Identity.** The definition's identifier — what tells this definition apart from every other one when
  something has to name it. Deciding an identity is choosing a label, not summarising what the definition
  says; a bad identity is one that tries to also carry the definition's name or its wording.

- **Name.** The human-readable label a person reads. Deciding a name is deciding what someone scanning a
  list of definitions would look for; nothing else here depends on it.

- **Abstract.** Whether no requirement is ever produced under this definition, only under the definitions
  that specialise it (K109). A definition is abstract only where it says so; an empty template is a
  template nobody has written yet, not a declaration. See below for what an abstract definition does not
  carry.

- **The wording template.** The structural pattern a requirement's wording is produced from, with places
  left for the definition's parameters. Writing this is deciding the sentence shape every requirement of
  this kind will share — not what any one requirement will say, which depends on the parameter values a
  particular requirement fills in later.

- **When it applies.** One sentence stating the circumstance under which this definition comes into play.
  It carries a claim of its own that is easy to get backwards — see below.

- **Parameters.** The variables a requirement of this kind fills in, each one naming the value domain it
  draws from and carrying an identity of its own (K106). Declaring a parameter is deciding what varies from
  one requirement of this kind to the next; which value domains exist for it to draw from is an
  implementation's business, exactly as which kinds exist is (K30). A definition also has every parameter
  its ancestors declare (K107) — see `specialisation-and-domains.md`.

- **What to ask.** For each parameter, how a non-expert is asked for the value that is missing. It is
  written once per parameter, not once per definition, and it is a rule in its own right — see below.

- **How it would be verified.** The method by which a requirement produced under this definition would be
  shown to hold, written once for the kind rather than once per requirement. It sits on the definition
  rather than on the requirement because a verification method is generic to a kind — a property of what
  sort of thing is being checked, not of the one instance in front of a reviewer — so a requirement produced
  under a definition that carries this inherits it without needing one of its own (K29).

- **The wording rule.** A well-formedness rule for the wording a requirement produced under this definition
  must satisfy. It stands on the same footing as *how it would be verified* — see below.

A bad attribute, on any of the nine, is one answering a different question than the one it was asked: a
name doing the work of an identity, a wording template trying to say when the definition applies, an
identity trying to describe what the definition is for. The nine stay separate because each is a separate
decision, and folding two into one field loses the record of which decision was actually made.

## A value comes from a source, and *what to ask* is how it is obtained

*Parameters* and *what to ask* do not take their meaning from any notation or design language. A value
exists only where a source states it (K125): somebody with standing said it, and the requirement records
who. Where nobody has, the value is missing — not assumed, not defaulted, and never supplied by the modeller,
who decides nothing for the project. An implementation's default is at most a suggestion the ask can carry,
and it becomes a value only when somebody states it (K127).

*What to ask* is how a missing value is obtained from somebody who holds it, and it is a rule (K116): where
a requirement of this kind has no value for the parameter, it raises a clarification, and where
requirements of this kind state different values of the parameter for the same thing, it raises a choice
for the project manager (K141). Write it as the question a non-expert can actually answer, addressed to
whoever would know.

This is also why *what to ask* is written per parameter and not once per definition. Each parameter can be
missing on its own, independently of the others, so each needs its own question — one *what to ask* per
parameter, not a single question trying to cover every gap a definition might ever have at once. A
parameter inherited from an ancestor brings its ask with it, and a descendant has none of its own for it
(K112): every descendant is after the same value.

## An abstract definition

An abstract definition exists so that the definitions beneath it share what it declares — its parameters,
above all, which every descendant has. Nothing is produced under it, so three of the nine do not apply
(K110): it carries no **wording template**, and neither **how it would be verified** nor the **wording
rule** applies to it, since all three speak of a requirement produced under the definition. The other six
apply as they do anywhere: it still says **when it applies**, which guides whoever is classifying a new
requirement down the tree, and every parameter it declares still needs its **what to ask**, because it is
filled through the definitions beneath.

A definition that is not abstract uses every parameter it has in its template, the inherited ones included
(K111): a value filled in that the wording never states would be a value the requirement carries silently.

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

This covers a definition's own nine attributes — phase 1. A `Rule`, and how one relates to a definition, is
phase 2, and is out of scope here.
