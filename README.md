# ProjectML skills

Agent skills for modelling with [ProjectML](https://github.com/szantob/ProjectML): turning what a modeller
knows — a conversation, a company's own documents, an existing package — into a valid implementation
package, and saying when the model is wrong.

**Status: in development.** Phase 1, domain design, is being built. What exists so far:

- `contract/` — what a valid package is: a JSON Schema for the written shape, the codes a checker may
  report, and a corpus of cases. A browser editor for the same packages is tested against it too, so the two
  cannot silently disagree about a package.
- `checker/` — a Python checker held to that contract. Install its dependencies with
  `python -m pip install -r checker/requirements.txt`, then run
  `python checker/check.py path/to/package.yaml`. It exits 0 for a package that fits the schema and raises
  no issue, 1 for one that does not fit the schema or that raises an issue — a misfit is as wrong as an
  issue — and 2 for a file it could not check at all.
- `skills/` — agent skills for building packages. The first is `domain-design/`, whose method is in
  `SKILL.md` and whose reference text is in `reference/`. It runs the checker to find what to ask back,
  and calls `python skills/domain-design/scripts/diagram.py path/to/package.yaml <identity>` to draw
  one kind's neighbourhood as a Mermaid class diagram. The script exits 0 for a diagram written, 1 for a
  subject it will not draw, and 2 for nothing to draw from — which includes a package that does not fit
  the schema, since there is then no subject to find in it. On exit 0 stdout is a Mermaid diagram, never a
  diagram plus something else: anything the script has to say about what it drew is a `%%` comment inside
  that same fence. On a non-zero exit it writes a sentence saying why, which is not a diagram.
  `python skills/domain-design/scripts/edit.py` changes a package's structure — extract, set, move,
  create, delete — carrying every kind's prose with what it moves, and prints the prose that may no
  longer hold where it now stands. It exits 0 when done, 1 when it refused rather than guess, and 2 for
  nothing to work from.

## The three phases

1. **Domain design** — the requirement kinds of a domain.
2. **Rule sets** — the rules over those kinds, and later over a project.
3. **Project modelling** — sources, needs, requirements and questions.

ProjectML is a metamodel and defines no notation. The YAML this repository works in is its own.
