---
name: domain-design
description: >
  Turn what a modeller knows about a domain -- the forms and models its project modelling ends in, a
  conversation, a company's own documents, or a package already begun -- into a complete, valid set of
  the requirement definitions (kinds) a client answers, and the tree of how they
  specialise one another, and change that tree later without losing what was written. Checks the work as
  it goes and asks back only what is actually missing, rather than guessing. Use this for domain design:
  deciding what kinds of requirement a domain has, writing each one's attributes, and extending or
  restructuring a domain that already exists.
---

# Domain design

A domain is grown and re-shaped, never designed in one pass. There are two decisions, taken again every
time anything is touched: **what is a kind and where does it sit**, and **what does it say**. Structure is
decided first where it is cheap to decide, and changed later with operations that carry every kind's prose
along with it -- never by rebuilding the tree, which throws the prose away.

Two processes follow. Use the first when there is no package yet, the second whenever one exists. Both
rest on one distinction, stated first, and on one question asked every time a kind is proposed.

## Project requirements, not requirement analysis

Two activities produce requirements, and only one of them is modelled here:

- **Project management** collects what the **client answers**: how many people, which date, what
  budget, which rooms. Every value in such a requirement is stated by somebody on the project's side,
  who is answerable for it. These are the kinds this skill designs.
- **Requirement analysis** works out, from the agreed baseline, the low-level requirements an
  implementation needs: how many pieces, which part, what rating. Its values are not answers but
  conclusions somebody draws for the implementation. That is design, beyond the seam, and it belongs to
  the next phase's model, not to this package.

**Ask it of every kind before it enters the package -- in the skeleton, while refining, and in every
change plan: *is this a project requirement or a derived one? Who answers it -- the client, or whoever
designs the implementation?*** Ask it of a parameter too: a value somebody would compute from other values
rather than be told is a derived one. When the answer is *derived*, say so to the modeller and leave it out
of the package; do not go looking for the answers to questions only the implementation asks. When the
answer is unclear, that is a question for the modeller, not a reason to model it just in case.

**A derived requirement left out need not be thrown away.** Offer to write the ones found as a by-product,
so that the next phase does not start from nothing -- and write it only if the modeller wants it. It is a
Markdown file beside the package, `derived-requirements.md` unless the modeller names another, with one
entry per requirement: what it would say, which project kind or kinds it is worked out from, and where it
was found. It is notes, not a model: it is not part of the package, nothing checks it, and nothing in the
package may depend on it. Add to it as the work goes; never move an entry back into the package without
asking the question above again.

Do not confuse this with ProjectML's *derivation* between requirements, which is a project requirement
too: an elaboration the client stated, beneath the requirement it elaborates.

## 1. Building a new model

1. **Ask first for the end product, before reading anything else.** Ask the modeller for whatever the
   finished project modelling must turn into, because that bounds what the domain needs and stops the
   search from running deep into questions nobody will ask:
   - **the model or document the next phase works from** -- what a designer or an implementer receives
     once the requirements are agreed;
   - **the forms and questionnaires used today** to take a project in -- briefs, order forms, intake
     checklists;
   - **a past project's filled-in version of either**, which shows which questions were really answered;
   - **what a quote or an offer has to know**, and **the acceptance or handover checklist**, where they
     exist -- the first bounds what must be asked, the second what must be verifiable.

   What the client is asked in these is the project side of the domain. What they work out from it is
   requirement analysis -- see above. When the modeller has none of it, skip this step and work from the
   conversation and whatever else they give.
2. **Read the domain as a whole and draw a shallow skeleton** -- the main kinds and their important
   sub-kinds, **two or three levels deep and no deeper**. Give each a **name** and a parent, and leave
   every other attribute blank. The name is not optional here: it is what a reviewer reads, so it must
   also be one no other kind in the package carries -- the checker raises `duplicate-kind-name` otherwise,
   and two sub-kinds both called *Other* under different parents are exactly that case. A skeleton
   this shallow is quick to review and makes the later work local. Draw it from the end product: a kind
   earns its place because the end product asks for it, and every kind passes the question above. Create
   each kind with `create` (see *The operations*), which generates its identity -- a UUID -- and prints
   it; never write an identity into the file by hand. Start from an empty package: `schemaVersion: 5`, a name, `version: ""`, and
   empty `valueDomains` and `kinds`.
3. **Show the skeleton to the modeller** and take their changes. Nothing is cheaper to change than a
   skeleton, so this is the place to argue about what the kinds are -- and which of them are derived.
4. **Work each kind out, top down** -- a parent before its children -- refining it with new sub-kinds
   only where the end product tells them apart: a sub-kind that the client would be asked nothing
   different for is not one. Work one kind at a time in a small context: `extract` it (see *The
   operations*) rather than reading the whole package. Write its attributes, reading
   `skills/domain-design/reference/requirement-definitions.md` first; use outside sources where the
   modeller offers them; show it to the modeller when they want to see it; run the checker after each.
   Top down, so that a child's prose can be **compared** with its parent's -- never copied from it (see
   *What this skill does not do*).
5. **When working a kind out shows the structure is wrong** -- it belongs elsewhere, or it is the same kind
   as another -- that is not a failure and not a reason to start over: run a small round of process 2 for
   that change, then carry on.
6. **When you are unsure whether a kind overlaps a sibling**, widen the context: extract its **parent**
   rather than the kind, which brings the siblings in. The shallow skeleton makes this rarely necessary; do
   it whenever it is.

## 2. Changing a model

For extending a domain and for restructuring one alike.

1. **Read the new need and find where it belongs.** First ask of it the question above: a need that only
   requirement analysis has is no change to this package. Then draft a change plan in terms of the
   operations: new kinds, an intermediate parent, moves, deletions. If the change is a restructuring, name it from
   `skills/domain-design/reference/restructuring.md` and follow its recipe where it has one.
2. **Show the plan to the modeller as structure only** -- which kinds appear, move or go, and under what --
   before anything runs. This is the cheap point again: nothing has been written against the new shape yet.
3. **Carry it out with the operations**, then run the checker.
4. **Judge every candidate the operations returned** (see *Candidates*), then work out the new kinds and
   any kind whose prose no longer holds, as in 1.4.

## The operations

    python scripts/edit.py extract PACKAGE SUBJECT OUTPUT
    python scripts/edit.py set     PACKAGE SUBJECT ATTRIBUTE VALUE
    python scripts/edit.py move    PACKAGE SUBJECT (--under TARGET | --to-root)
    python scripts/edit.py create  PACKAGE (--under PARENT | --at-root) [--name NAME]
    python scripts/edit.py delete  PACKAGE SUBJECT
    python scripts/edit.py add-parameter PACKAGE SUBJECT --name NAME [--domain ID] [--ask TEXT]

- **extract** writes the subject's subtree, its ancestor chain and the value domains they use to a new
  package at OUTPUT, which the checker can check on its own. The source is not touched. This is the small
  context of 1.4.
- **set** writes one prose attribute -- `name`, `text`, `whenItApplies`, `howItWouldBeVerified` or
  `wordingRule` -- exactly as given. A VALUE of `-` is read from stdin, for prose of several lines. It
  also sets `abstract`, to `true` or `false`. It refuses the identity: **no operation edits an
  identity**. It refuses `specialises`: that is a move.
- **move** cuts the subject **with everything beneath it** and pastes it under the target, or at the root
  level. Every kind moved keeps every attribute; only the subject's parent changes. Since a kind has
  every parameter its ancestors declare, it notes the parameters the subtree loses and gains.
- **create** adds one new kind under a parent or at the root level, with a generated identity, the name
  given and nothing else. It is not abstract. It prints the identity, which later operations need.
- **delete** removes the subject **with everything beneath it**, so nothing is left pointing at a kind that
  is gone.
- **add-parameter** adds one parameter to the subject, with a generated identity and the name, value
  domain and *what to ask* given. It prints the identity. The name is what the template writes in a
  placeholder; every kind beneath the subject has the parameter too.

A parameter's other attributes, rules and value domains are structured rather than prose, and no operation
writes them yet; write those in the package file directly -- never an identity -- and run the checker after.

There is no operation that moves or deletes a kind without its children. Where the children should go
somewhere else, move them there first, one subtree at a time; then the kind is a leaf, and moving or
deleting it takes nothing else with it.

Every operation names kinds by identity and needs each identity to name exactly one kind. When none does,
or more than one does, it **refuses and changes nothing** rather than picking one; tell the modeller which.
Exit status: **0** done (or nothing needed changing), **1** refused, **2** nothing to work from -- the file
is unreadable, is not YAML, or does not fit the schema.

## Candidates

What an operation prints after what it did is in two parts. **Notes** are facts about structure the
checker will also report -- a rule outside a deleted subtree that implies a kind now gone. **Candidates**
are prose that may no longer hold where it now stands: a subtree that arrived under new ancestors with its
prose unchanged, prose that mentions an ancestor the kind no longer has, prose still using a name that was
changed, prose mentioning a kind that was deleted.

A candidate is **raw material for an opinion, not one**. The script matches text; it does not know what
the text means. Read each one against the kind it names and decide whether the prose still holds. If it
does not, report that as an opinion, in the third register below -- with what would settle it -- and
propose the new wording for the modeller to accept. A candidate that turns out to be nothing is dropped
without mention. The script never writes prose of its own; neither does an opinion, until the modeller
accepts it.

## Let the checker drive what is asked back

Run the checker after each kind is worked out and after each change (the paths below are relative to this
skill's directory, because the working directory will be the package's, not the skill's):

    python ../../checker/check.py path/to/package.yaml

That is where the checker is when the skill came with its repository, as a plugin. When it came as the
bundle uploaded to claude.ai, the checker travels inside the skill, and the command is
`python checker/check.py path/to/package.yaml`: use whichever of the two exists. The scripts find it in
either place on their own.

The checker and both scripts require Python with `PyYAML` and `jsonschema` installed; if either is missing,
they say so, name what to install, and exit 2. Ask the modeller before installing anything. Its findings decide what is asked back -- the questions come from the package's
own holes, not from memory of what a package usually needs. This has a limit at the very start: an empty
package raises no issue and has no gaps, because there is nothing yet for the checker to measure. So the
skeleton is driven by the end product asked for in 1.1, and by whatever else the modeller has given -- a
conversation, documents -- not by the checker. Once kinds exist, the checker takes over. Neither ever
decides that a kind belongs: a gap on a derived kind is no reason to fill it, only to take the kind out.

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
  view, wrong: broader than it should be, oddly worded, short of what it needs to say, or no longer true
  where an operation put it. An opinion carries **no code**. It never shares a list or a count with the
  issues or the gaps, and it is reported **after** both. It always **names what would settle it** -- what
  to ask the modeller, or what to check the prose against. An opinion never acts on its own: it may be
  proposed, and nothing it proposes enters the package until the modeller accepts it.

## When the work is done

The skill's work is finished when the checker raises no issue, the modeller has seen and answered every gap
(either by filling it or by choosing to leave it unsaid), and the modeller has answered every opinion the
skill raised. A remaining gap is not, by itself, a reason to keep going: a gap is something not yet said, and
a modeller is free to decide it stays unsaid. The work ends when nothing is left that the modeller has not
seen and either acted on or deliberately declined.

## When to draw

`skills/domain-design/scripts/diagram.py` is a separate function, callable whenever a picture of one kind's
neighbourhood is useful -- while the skeleton takes shape, after working a kind out, before and after a
change, or on a package that already exists, before touching it:

    python scripts/diagram.py path/to/package.yaml <identity>

It draws one subject at a time: exit 0 means a diagram was written for it, exit 1 means the subject given
will not be drawn, exit 2 means there was nothing to draw from at all. Drawing a whole domain -- walking
every kind and drawing each one -- is this skill's own job, done by calling the script once per subject; it
has no whole-package mode of its own. On exit 0 its stdout is one Mermaid class diagram, never a diagram plus
something else: anything it has to say about what it could not draw -- a missing parent, an identity shared
by two drawn kinds -- is a `%%` comment inside that same fence. Relay that comment to the modeller. On a
non-zero exit it writes a sentence saying why, which is not a diagram.

## The three reference files

Read `skills/domain-design/reference/requirement-definitions.md` before writing or judging any of a kind's
nine attributes -- it says what each one means, not what shape it takes on the page.

Read `skills/domain-design/reference/specialisation-and-domains.md` before drawing, proposing, or judging
the edge between two kinds, or the value domain a parameter draws from.

Read `skills/domain-design/reference/restructuring.md` before planning any change that moves, merges,
splits or removes existing kinds -- it names the restructurings there are and gives a recipe for the four
whose effect on prose no operation reports.

## What this skill does not do

Decline these rather than drift into them:

- **Requirement analysis.** Kinds and parameters whose values somebody works out from the baseline for an
  implementation -- see *Project requirements, not requirement analysis*. Name such a kind to the
  modeller as derived, and leave it to the next phase's model, noted in the optional by-product at most.
- **Rules.** A kind's `rules` stays empty here. Rules are phase 2.
- **Project modelling.** Sources, needs, requirements and questions belong to phase 3.
- **Answering an open metamodel question for convenience.** Where the metamodel leaves something open --
  whether an inherited parameter may be narrowed, whether a wording rule or a verification method is
  inherited -- do not settle it because a package needs an answer now. Say that it is open, and act
  consistently with that: for instance, never copy an ancestor's prose down the tree, and never delete a
  child's statement because its parent now says the same. Parameters are the one thing that *is*
  inherited, and that is decided: never redeclare an ancestor's parameter on a descendant.
