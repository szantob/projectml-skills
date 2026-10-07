"""Build the domain-design skill as one ZIP a claude.ai upload accepts.

    python release/bundle.py OUTPUT_DIRECTORY

claude.ai takes a skill as a ZIP holding one folder, and uploads nothing
outside that folder. In this repository the skill's scripts lean on the
checker beside skills/, and the checker on the contract beside it, so the
bundle carries both inside the skill:

    domain-design/
        SKILL.md, reference/, scripts/
        checker/
        contract/

The scripts look for the checker inside the skill first (see
``dependencies.py``), and the checker finds the contract one level above
itself in either layout, so nothing is edited on the way in. Tests and the
conformance corpus stay behind: they check this repository, not a package.

The ZIP is the same bytes for the same commit: entries are sorted and carry
one fixed time, so a rebuilt bundle can be compared with a released one.

The exit status is 0 when the ZIP was written, 2 when it could not be.
"""

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = "domain-design"
NAME = f"{SKILL}.zip"

# What goes in, as (where it is in this repository, where it goes inside the
# skill's folder). A directory goes in whole, less what LEFT_OUT names.
PARTS = (
    (Path("skills") / SKILL / "SKILL.md", Path("SKILL.md")),
    (Path("skills") / SKILL / "reference", Path("reference")),
    (Path("skills") / SKILL / "scripts", Path("scripts")),
    (Path("checker"), Path("checker")),
    (Path("contract") / "package.schema.json", Path("contract/package.schema.json")),
    (Path("contract") / "vocabulary.json", Path("contract/vocabulary.json")),
    (Path("contract") / "README.md", Path("contract/README.md")),
)

# Directories that belong to working on this repository, not to using the
# skill, and the one file the checker keeps for that work alone.
LEFT_OUT_DIRECTORIES = {"tests", "__pycache__", ".pytest_cache"}
LEFT_OUT_FILES = {"requirements-dev.txt"}

# The earliest time a ZIP entry can carry.
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def entries(root=ROOT):
    """Every file the bundle holds, as (source path, name inside the ZIP),
    sorted by that name."""
    found = []
    for source, inside in PARTS:
        source = root / source
        if source.is_file():
            found.append((source, inside))
            continue
        for path in source.rglob("*"):
            relative = path.relative_to(source)
            if not path.is_file():
                continue
            if LEFT_OUT_DIRECTORIES.intersection(relative.parts[:-1]):
                continue
            if path.name in LEFT_OUT_FILES or path.suffix == ".pyc":
                continue
            found.append((path, inside / relative))
    return sorted(
        ((path, (Path(SKILL) / inside).as_posix()) for path, inside in found),
        key=lambda entry: entry[1],
    )


def build(output_directory, root=ROOT):
    """Write the bundle into ``output_directory`` and return its path."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    target = output_directory / NAME
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as bundle:
        for source, name in entries(root):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, source.read_bytes())
    return target


def main(arguments):
    if len(arguments) != 1:
        print("Usage: python release/bundle.py OUTPUT_DIRECTORY")
        return 2
    try:
        target = build(arguments[0])
    except OSError as error:
        print(f"The bundle could not be written: {error}")
        return 2
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
