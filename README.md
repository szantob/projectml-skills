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
  no issue, 1 for one that does not, and 2 for a file it could not check.

- `skills/` — the skills themselves, beginning with `domain-design/`. Its `scripts/diagram.py` draws one
  kind's neighbourhood as a Mermaid class diagram: run
  `python skills/domain-design/scripts/diagram.py path/to/package.yaml <identity>`. It exits 0 having
  drawn, 1 for a subject it cannot draw truthfully, and 2 if the file could not be read or the document
  it holds does not fit the schema.

## The three phases

1. **Domain design** — the requirement kinds of a domain.
2. **Rule sets** — the rules over those kinds, and later over a project.
3. **Project modelling** — sources, needs, requirements and questions.

ProjectML is a metamodel and defines no notation. The YAML this repository works in is its own.
