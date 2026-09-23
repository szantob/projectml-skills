---
name: domain-design
description: >
  Turn what a modeller knows about a domain -- a conversation, a company's own documents, or a package
  already begun -- into a complete, valid set of requirement definitions (kinds) and the tree of how they
  specialise one another. Checks the work as it goes and asks back only what is actually missing, rather
  than guessing. Use this for domain design: deciding what kinds of requirement a domain has, and writing
  each one's attributes.
---

# Domain design

## The two passes

Build a package in two passes, not one.

First, the **skeleton**: propose which kinds exist and how they specialise one another, and nothing else --
an identity and a parent for each, every other attribute left blank. Show the proposal to the modeller and
let them accept it or rewrite it before going further. Deciding what counts as a kind at all is the
expensive judgement; a skeleton carries no prose, so rewriting it throws nothing away.

Only once the skeleton holds, do the **filling**, kind by kind: name, wording template, when it applies,
parameters (each naming the value domain it draws from), what to ask (each per parameter, the question that
turns an unknown value into a known one), how it would be verified, and the wording rule. Read
`skills/domain-design/reference/requirement-definitions.md` first -- see below.

## Starting from a package that already exists

When the modeller already has a package, do not run a different procedure for it: seed the same two-pass
procedure with it instead of starting from nothing. Check it first (see the next section) to see where it
stands, then treat its existing kinds as the skeleton pass's starting point.

## Let the checker drive what is asked back

Run the checker at the end of each pass:

    python checker/check.py path/to/package.yaml

Its findings decide what is asked back -- the questions come from the package's own holes, not from memory
of what a package usually needs. This has a limit at the very start: an empty package raises no issue and
has no gaps, because there is nothing yet for the checker to measure. So the skeleton pass, run from
nothing, is driven by whatever the modeller has given -- a conversation, documents -- not by the checker.
Once kinds exist, the checker takes over, and its output is what drives the rest of both passes.

## What the checker's exit status means

`checker/check.py` exits with one of three statuses, and each calls for something different:

- **0** -- the package fits the contract's schema and raises no issue. It may still have gaps; read them
  (see the three registers, below) and turn them into what is asked back.
- **1** -- the package does not fit the schema, or fits it but raises an issue. Either way the package
  itself is wrong and must be fixed before anything else proceeds: a misfit or an issue is a defect in what
  was written, not a question to put to the modeller.
- **2** -- the file could not be checked at all. This is not a verdict on the package. Resolve whatever
  stopped the checker (a missing dependency, a file it could not read) and run it again.

## The three registers

Keep three things apart, and keep them apart structurally -- by where each is reported, not by how it is
worded:

- An **issue** is measured by the checker and carries one of its vocabulary codes.
- A **gap** is measured too, coded by field rather than by an issue code, and it **is not a fault** -- the
  checker exits 0 on a package that has gaps. A gap is exactly the list worth asking the modeller about.
- An **opinion** is the skill's own judgement about a piece of prose that is present but, in the skill's
  view, wrong: broader than it should be, oddly worded, short of what it needs to say. An opinion carries
  **no code**. It never shares a list or a count with the issues or the gaps, and it is reported **after**
  both. It always **names what would settle it** -- what to ask the modeller, or what to check the prose
  against. An opinion never acts on its own: it may be proposed, and nothing it proposes enters the package
  until the modeller accepts it.

## When the work is done

The skill's work is finished when the checker raises no issue, the modeller has seen and answered every gap
(either by filling it or by choosing to leave it unsaid), and the modeller has answered every opinion the
skill raised. A remaining gap is not, by itself, a reason to keep going: a gap is something not yet said, and
a modeller is free to decide it stays unsaid. The work ends when nothing is left that the modeller has not
seen and either acted on or deliberately declined.

## When to draw

`skills/domain-design/scripts/diagram.py` is a separate function, callable whenever a picture of one kind's
neighbourhood is useful -- during the skeleton pass to show the tree taking shape, after filling in a kind,
or on a package that already exists, before touching it:

    python skills/domain-design/scripts/diagram.py path/to/package.yaml <identity>

It draws one subject at a time: exit 0 means a diagram was written for it, exit 1 means the subject given
will not be drawn, exit 2 means there was nothing to draw from at all. Drawing a whole domain -- walking
every kind and drawing each one -- is this skill's own job, done by calling the script once per subject; it
has no whole-package mode of its own. Its stdout is always one Mermaid class diagram, never a diagram plus
something else: anything it has to say about what it could not draw -- a missing parent, an identity shared
by two drawn kinds -- is a `%%` comment inside that same fence. Relay that comment to the modeller.

## The two reference files

Read `skills/domain-design/reference/requirement-definitions.md` before writing or judging any of a kind's
eight attributes -- it says what each one means, not what shape it takes on the page.

Read `skills/domain-design/reference/specialisation-and-domains.md` before drawing, proposing, or judging
the edge between two kinds, or the value domain a parameter draws from.

## What this skill does not do

Decline these rather than drift into them:

- **Rules.** A kind's `rules` stays empty here. Rules are phase 2.
- **Project modelling.** Sources, needs, requirements and questions belong to phase 3.
- **Answering an open metamodel question for convenience.** Where the metamodel leaves something open --
  whether specialisation inherits an ancestor's values, whether a value domain fixes a unit -- do not settle
  it because a package needs an answer now. Say that it is open, and act consistently with that: for
  instance, never copy an ancestor's value down the tree.
