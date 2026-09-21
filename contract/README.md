# The package contract

What a valid ProjectML implementation package is, stated once and used by two implementations: the
browser editor, in TypeScript, and the agent skill's checker, in Python. Each is tested against this
directory, so if the two ever disagree about a package, a test fails instead of a modeller getting two
answers to one question.

This is the editor's notation, not ProjectML's. ProjectML is a metamodel and has no notation.

## What is here

- `package.schema.json` — the written shape of a package, schema version 3. **Strict**: every attribute
  is required and no other attribute is allowed. An agent adding an attribute of its own would be
  inventing metamodel, so the schema refuses it.
- `vocabulary.json` — the issue codes and gap fields a checker may report, each with a gloss saying exactly
  when it is reported and how often. Implementations are compared on the codes and fields, never on the
  wording of their messages.
- `conformance/` — cases. Each directory holds a `package.yaml` and an `expected.json` saying whether the
  package fits the schema and, if it does, which issues and gaps it has.

## Reading the YAML

A package is YAML 1.2, read with the core schema. Every consumer must read a file the same way, or two
implementations can disagree about what a file says before any rule is applied to it:

- A file is exactly one document, and its root is a mapping. A second document is an error.
- A key repeated within one mapping is an error, not a silent overwrite.
- `<<` is an ordinary key. Merge keys are not expanded.
- `on`, `off`, `yes` and `no` are strings, not booleans.
- An unquoted number is a number: `010` reads as ten and `1.0` as one. A number where the schema wants a
  string fails the schema, so an identity or a version that looks numeric must be quoted.
- A date-like scalar such as `2026-09-19` is a string.
- A document that contains an alias is unreadable. An anchor that is never aliased changes nothing and is
  read as if it were absent, and that holds however many anchors share a name: without an alias, no name is
  ever looked up.
- A document that declares a YAML version with `%YAML`, or that gives any node an explicit tag, is
  unreadable. The rules above all say what a value means when it is left to the reader to work out; an
  explicit tag such as `!!bool` overrides that reasoning, and a version directive replaces the rules it
  reasons by. A package needs neither: it is written by a tool, for a tool. A `%TAG` directive alone
  declares a shorthand and changes nothing, since using it would require the explicit tag this refuses.

YAML 1.1 differs on most of these points, and PyYAML's `safe_load` implements YAML 1.1. A consumer must use
a reader that follows the rules above, whatever language it is written in.

## How a case is compared

- A case first says whether its file can be read at all. `"parses": false` marks one that cannot, and such a
  case carries nothing else. A case that can be read omits `parses`, and says whether it fits the schema.
- Issues are compared as a code and the kind they name — or `null`, for an issue about the package as a
  whole. Gaps are compared as a kind, a field, and, for a *what to ask* gap, the parameter.
- Results are compared as multisets: how many times an entry appears counts, the order it appears in does
  not. Two entries alike in every compared part are two results, not one — a checker that reports one where
  a case expects two does not conform. Several glosses say how often a finding is reported, and this is
  what makes those sentences testable.
- A case that does not fit the schema is compared on that verdict alone, and carries no issues or gaps:
  anything written beside the verdict would be asserting nothing, so a test refuses it.
- Kinds are named by identity because that is how the reports name them. Identities are free text and need
  not be unique; the corpus includes a case where two kinds share one.

## Rules for adding a case

- **Invent it.** No case may contain, quote or paraphrase a real organisation's package.
- Every issue code and every gap field must appear in at least one case, and a test enforces this. That is
  the floor, not the aim: **every rule needs at least one case that separates it from its likeliest wrong
  reading**, so that an implementation getting the rule wrong reaches a different verdict somewhere.
- YAML is indented with spaces. Quote prose, so a colon or a brace in it cannot change the document's
  structure.

## Where this lives

This directory is part of the public ProjectML skills repository, beside the checker tested against it. The
browser editor takes it as a git submodule. Nothing here may refer to anything outside this directory.
