"""Reading and writing a package's YAML, the one writer on the Python side.

Reading is the checker's: ``dialect.load``, so that what an operation reads
is what the checker reads. Writing is here, and holds the rules the contract
puts on whatever writes a package:

- text holding U+0085, U+2028 or U+2029 is quoted, because the dialect
  refuses those three outside quotes;
- no anchor is written, because the dialect refuses every alias;
- a string the core schema would read as something else - ``null``,
  ``0o17``, ``1e3`` - is quoted, because PyYAML's emitter asks YAML 1.1
  which scalars need quoting, and 1.1 does not know those three.

Beyond the rules, two choices for the reader of the file: multi-line prose
is a literal block where YAML allows one, and no line is folded, so a moved
kind's prose reads the same, line for line, after the move.
"""

import os
import sys
import tempfile
from pathlib import Path

import yaml

# Run as a script, this file's own directory is the only thing on the path;
# the checker's reader is four levels up. See diagram.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "checker"))

import dialect  # noqa: E402

NON_ASCII_LINE_BREAKS = dialect.NON_ASCII_LINE_BREAKS


class _Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def increase_indent(self, flow=False, indentless=False):
        # A list under a key is indented beneath it, as the contract's own
        # cases are written, rather than flush with the key.
        return super().increase_indent(flow, False)


# The emitter quotes a string exactly when a resolver would read the plain
# scalar as something else. Its resolvers are YAML 1.1's; the dialect's are
# the 1.2 core schema's. Both sets are asked, so a string is quoted when
# either reader would take it for a non-string - quoting one more than needed
# costs nothing, quoting one fewer changes what the file says.
for _first, _resolvers in dialect._Loader.yaml_implicit_resolvers.items():
    for _tag, _pattern in _resolvers:
        _Dumper.add_implicit_resolver(_tag, _pattern, [_first])


def _represent_str(dumper, value):
    if any(ch in value for ch in NON_ASCII_LINE_BREAKS):
        style = '"'
    elif "\n" in value:
        # A request, not an order: the emitter falls back to quoting where a
        # literal block cannot hold the text, trailing spaces for one.
        style = "|"
    else:
        style = None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


_Dumper.add_representer(str, _represent_str)


def dump(document):
    """``document`` as YAML text in the contract's dialect."""
    return yaml.dump(
        document,
        Dumper=_Dumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        # No line is folded: a folded line reads back the same, but it moves
        # when a word before it changes, and prose that did not change should
        # not look as if it had.
        width=float("inf"),
    )


def read(path):
    """The document in the file at ``path``, read by the dialect.

    Raises ``dialect.Unreadable``, ``OSError`` or ``UnicodeDecodeError``.
    """
    return dialect.load(Path(path).read_text(encoding="utf-8"))


def write(path, document):
    """Replace the file at ``path`` with ``document``, all at once.

    Written beside the file and then moved over it, so a failure half-way
    leaves the old file rather than half a new one.
    """
    path = Path(path)
    text = dump(document)
    handle, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
            out.write(text)
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.remove(temporary)
        raise
