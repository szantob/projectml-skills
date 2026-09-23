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

## An identifier is not a key

A kind's identity, and a value domain's, is a free-text attribute the user edits, so it is never unique: two
may carry the same one, and one may be empty or name a parent that does not exist. Code addresses a kind by
its position in the package's `kinds` list, or by object identity, never by its id: an id is fine for saying
what a `specialises` names, but it is no map key, no dictionary key, and no way to tell two kinds apart.
This is why `tree.py` speaks in positions throughout, and why a shared identity draws nothing rather than
picking one of the kinds that carry it.

## The contract

`contract/` is shared by two implementations, so a change to it is a change to both. When a case is added or
the schema changes, the editor follows in its own repository, and the checker here must pass the whole
corpus. Cases are compared on codes and fields, never on the wording of a message — see
`contract/README.md`.

## House rules

- English everywhere: code, comments, messages, commit messages.
- Python follows PEP 8, with four-space indentation and a line of at most 88 characters. `ruff.toml` holds
  the rule and the workflow runs `ruff check`, so this is a sentence a reader can check rather than trust.
  There is no formatter: the checker is read the way its prose is read, and where a line breaks is the
  author's.
- JSON is indented with tabs. YAML is indented with two spaces, because YAML forbids tabs.
- Commit after every task. Never push.
