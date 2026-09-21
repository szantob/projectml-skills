"""Check a ProjectML implementation package against the contract.

    python checker/check.py path/to/package.yaml

A JSON package can be checked too: JSON is a subset of YAML 1.2.

The exit status says what kind of answer this is:

    0   the package fits the schema and raises no issue — gaps or not, since a
        gap is something not yet said rather than something wrong
    1   the package does not fit the schema, or raises an issue
    2   the file could not be checked at all
"""

import sys
from pathlib import Path

REQUIREMENTS = Path(__file__).resolve().parent / "requirements.txt"

try:
    import contract_schema
    import dialect
    import findings
except ImportError as error:
    print(
        f"The checker needs PyYAML and jsonschema, and {error.name} is missing. "
        f"Install them with: python -m pip install -r {REQUIREMENTS}"
    )
    sys.exit(2)


def check(text, out):
    """Check the package in ``text``, write the report to ``out``, and return
    the exit status."""
    try:
        document = dialect.load(text)
    except dialect.Unreadable as error:
        out.write(f"Cannot be read: {error}\n")
        return 2

    wrong = contract_schema.misfits(document)
    if wrong:
        out.write("Does not fit the schema:\n")
        for line in wrong:
            out.write(f"  - {line}\n")
        return 1

    out.write("Fits the schema.\n")

    found = findings.issues(document)
    if found:
        out.write(f"Issues ({len(found)}):\n")
        for issue in found:
            where = "" if issue.kind is None else f" [kind {issue.kind!r}]"
            out.write(f"  - {issue.code}{where}: {issue.message}\n")
    else:
        out.write("No issues.\n")

    holes = findings.gaps(document)
    if holes:
        out.write(f"Gaps ({len(holes)}):\n")
        for gap in holes:
            which = "" if gap.parameter is None else f" (parameter {gap.parameter!r})"
            out.write(f"  - kind {gap.kind!r}: {gap.field}{which}\n")
    else:
        out.write("No gaps.\n")

    return 1 if found else 0


def main(argv):
    # A package may hold any language; a Windows console does not default to
    # one that can print it.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print("Usage: python checker/check.py path/to/package.yaml")
        return 2
    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as error:
        print(f"Cannot be read: {error}")
        return 2
    except UnicodeDecodeError:
        # A file in some other encoding is not a package this checker can
        # read, and saying so is not the same answer as "the package is
        # wrong": it must not reach the exit status that means it is.
        print(f"Cannot be read: {argv[1]} is not UTF-8 text.")
        return 2
    return check(text, sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
