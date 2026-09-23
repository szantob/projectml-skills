"""Edit a package's structure without losing its prose.

    python skills/domain-design/scripts/edit.py COMMAND ...

    extract PACKAGE SUBJECT OUTPUT
    set     PACKAGE SUBJECT ATTRIBUTE VALUE
    move    PACKAGE SUBJECT (--under TARGET | --to-root)
    create  PACKAGE (--under PARENT | --at-root) [--name NAME]
    delete  PACKAGE SUBJECT

SUBJECT, TARGET and PARENT are identities. For ``set``, a VALUE of ``-`` is
read from stdin, less one final line break, so prose of several lines need
not pass through a command line.

The package is edited in place. ``extract`` writes a new package to OUTPUT
and leaves the source alone. What each operation guarantees is in
``operations.py``.

stdout says what was done, then any **notes** - facts about the structure the
checker will also report - and then any **candidates**: prose that may no
longer hold where it now stands. A candidate carries no code and is not a
finding; it is for the agent to judge.

The exit status says what kind of answer this is:

    0   done - the package was written, or there was nothing to change
    1   refused - the operation would have had to guess; nothing was written
    2   nothing to work from - unreadable, not YAML, or not the schema's shape
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "checker"))

import contract_schema  # noqa: E402
import dialect  # noqa: E402
import operations  # noqa: E402
import package_io  # noqa: E402


def _parser():
    parser = argparse.ArgumentParser(
        prog="edit.py", description="Edit a package's structure."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    extract = commands.add_parser("extract", help="write a subtree as a package")
    extract.add_argument("package")
    extract.add_argument("subject")
    extract.add_argument("output")

    set_ = commands.add_parser("set", help="set one prose attribute")
    set_.add_argument("package")
    set_.add_argument("subject")
    set_.add_argument("attribute")
    set_.add_argument("value")

    move = commands.add_parser("move", help="move a subtree")
    move.add_argument("package")
    move.add_argument("subject")
    where = move.add_mutually_exclusive_group(required=True)
    where.add_argument("--under", metavar="TARGET")
    where.add_argument("--to-root", action="store_true")

    create = commands.add_parser("create", help="create a kind")
    create.add_argument("package")
    where = create.add_mutually_exclusive_group(required=True)
    where.add_argument("--under", metavar="PARENT")
    where.add_argument("--at-root", action="store_true")
    create.add_argument("--name", default="")

    delete = commands.add_parser("delete", help="delete a subtree")
    delete.add_argument("package")
    delete.add_argument("subject")
    return parser


def _load(path, out):
    """The document at ``path``, or ``None`` having said why not."""
    if path.suffix.lower() == ".json":
        # Written back, it would be YAML under a .json name.
        out.write(
            f"Cannot be edited: {path} is JSON, and this writes YAML. Export "
            f"the package as YAML first.\n"
        )
        return None
    try:
        document = package_io.read(path)
    except OSError as error:
        out.write(f"Cannot be read: {error}\n")
        return None
    except UnicodeDecodeError:
        out.write(f"Cannot be read: {path} is not UTF-8 text.\n")
        return None
    except dialect.Unreadable as error:
        out.write(f"Cannot be read: {error}\n")
        return None
    wrong = contract_schema.misfits(document)
    if wrong:
        out.write("Does not fit the schema:\n")
        for line in wrong:
            out.write(f"  - {line}\n")
        return None
    return document


def _value(given, stdin):
    if given != "-":
        return given
    text = stdin.read()
    if text.endswith("\r\n"):
        return text[:-2]
    if text.endswith("\n"):
        return text[:-1]
    return text


def _report(result, out):
    out.write(f"{result.summary}\n")
    if result.notes:
        out.write("Notes:\n")
        for note in result.notes:
            out.write(f"  - {note}\n")
    if result.candidates:
        out.write("Candidates, for the agent to judge - none is a finding:\n")
        for candidate in result.candidates:
            out.write(f"  - {candidate}\n")


def run(argv, out, stdin):
    """Run the command in ``argv`` (without the program name), and return
    the exit status."""
    try:
        args = _parser().parse_args(argv)
    except SystemExit as stop:
        return 2 if stop.code else 0

    path = Path(args.package)
    document = _load(path, out)
    if document is None:
        return 2

    try:
        if args.command == "extract":
            output = Path(args.output)
            if output.exists():
                out.write(f"{output} already exists; an extract never overwrites.\n")
                return 1
            result = operations.extract(document, args.subject)
        elif args.command == "set":
            value = _value(args.value, stdin)
            result = operations.set_attribute(
                document, args.subject, args.attribute, value
            )
        elif args.command == "move":
            target = None if args.to_root else args.under
            result = operations.move(document, args.subject, target)
        elif args.command == "create":
            parent = None if args.at_root else args.under
            result = operations.create(document, parent, args.name)
        else:
            result = operations.delete(document, args.subject)
    except operations.Refused as refusal:
        out.write(f"{refusal}\n")
        return 1

    if result.changed:
        destination = Path(args.output) if args.command == "extract" else path
        package_io.write(destination, result.document)
    _report(result, out)
    return 0


def main():
    # A package may hold any language; a Windows console does not default to
    # one that can print it, or read it.
    for stream in (sys.stdout, sys.stdin):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    return run(sys.argv[1:], sys.stdout, sys.stdin)


if __name__ == "__main__":
    sys.exit(main())
