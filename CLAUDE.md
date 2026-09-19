# CLAUDE.md

Conventions for anyone — human or agent — working in this repository.

## What this repository is

Public agent skills for ProjectML, and the contract they share with a browser editor. It is developed as a
git submodule of that editor's repository, which is private.

## Nothing private enters this repository

It is public, and its history is permanent. Nothing belonging to the private side may enter it:

- **No real organisation's package** — not whole, not in pieces, not "anonymised". Every example and every
  conformance case is invented.
- **No reference to the private repository's contents** — its paths, its design records, its notes.
- **Commit messages count.** They are published with the history.

## Push this repository first

The editor records which commit of this repository it was tested against. Push this repository before the
editor's, or the editor will point at a commit GitHub does not have yet. Pushing is the owner's decision;
an agent never pushes.

## The contract

`contract/` is shared by two implementations, so a change to it is a change to both. When a case is added or
the schema changes, the editor follows in its own repository, and the checker here must pass the whole
corpus. Cases are compared on codes and fields, never on the wording of a message — see
`contract/README.md`.

## House rules

- English everywhere: code, comments, messages, commit messages.
- Python follows PEP 8, with four-space indentation. JSON is indented with tabs. YAML is indented with two
  spaces, because YAML forbids tabs.
- Commit after every task. Never push.
