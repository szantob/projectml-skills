"""Reading a package's YAML the way the contract says it is read.

PyYAML's safe loader implements YAML 1.1, and the contract's dialect is YAML 1.2
read with the core schema. They differ on six points, each corrected here:

- a key repeated within one mapping is an error, not a silent overwrite;
- ``<<`` is an ordinary key, so merge keys are not expanded;
- only ``true`` and ``false`` are booleans, so ``on`` and ``yes`` stay strings;
- integers and floats follow the core schema, so ``010`` is ten, not eight;
- a date-like scalar is a string, not a date;
- a document that contains an alias is unreadable.

Two things the dialect refuses outright are corrected here too, because the
library allows both: an explicit tag on any node, and a `%YAML` directive. Each
of the six rules above says what a value means when the reader is left to work
it out, and both of these take that decision away from it.

Every correction is pinned by a case in the contract's corpus and by a test of
its own, because a reader that silently disagrees with the contract is the one
failure a checker must not have.
"""

import re
from collections import abc

import yaml


class Unreadable(Exception):
    """The file is not a YAML document this contract can read."""


class _Loader(yaml.SafeLoader):
    """SafeLoader with YAML 1.1's resolvers replaced by the 1.2 core schema's."""

    def scan_line_break(self):
        # YAML 1.2 has two line breaks, the line feed and the carriage return;
        # U+0085, U+2028 and U+2029 were breaks in 1.1 and are ordinary
        # characters from 1.2 on, for JSON's sake. The library keeps the last
        # two as themselves already, and turns U+0085 into a line feed — which
        # a quoted scalar then folds to a space, so a name written as a single
        # U+0085 arrived here unwritten and reached the other implementation
        # as the character it was.
        #
        # Returning it as itself is the whole correction. It must still be
        # consumed: the scanner tests for the wider set in a dozen places and
        # loops forever on a character it thinks is a break and cannot pass.
        # The line number in an error's mark still counts it as a break, and
        # no rule of this contract reads that.
        if self.peek() == "\x85":
            self.forward()
            return "\x85"
        return super().scan_line_break()

    def process_directives(self):
        result = super().process_directives()
        # A version directive replaces the rules this dialect reasons by, so a
        # document carrying one is outside the dialect rather than a document
        # to be read by other rules. A %TAG directive alone declares a
        # shorthand and changes nothing, because using it would need the
        # explicit tag `compose_node` refuses.
        if self.yaml_version is not None:
            declared = ".".join(str(part) for part in self.yaml_version)
            raise yaml.parser.ParserError(
                None,
                None,
                f"a package declares no YAML version, and this one declares "
                f"{declared}",
                None,
            )
        return result

    def compose_node(self, parent, index):
        # An alias makes the document unreadable.
        if self.check_event(yaml.AliasEvent):
            event = self.peek_event()
            raise yaml.composer.ComposerError(
                None, None, "a package contains no aliases", event.start_mark
            )

        event = self.peek_event()

        # Every rule of this dialect says what a value means when the reader is
        # left to work it out. An explicit tag overrides that reasoning, so a
        # document carrying one is outside the dialect. A node whose tag was
        # resolved implicitly carries none on its event at all.
        if getattr(event, "tag", None) is not None:
            raise yaml.composer.ComposerError(
                None,
                None,
                f"a package gives no node an explicit tag, and this one has "
                f"{event.tag!r}",
                event.start_mark,
            )

        # An anchor that is never aliased is read as if it were absent, and
        # every alias is refused above, so no anchor is ever looked up.
        # Forgetting them is what lets two of them share a name, which the
        # library would otherwise refuse.
        self.anchors.clear()

        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            # A key that is a sequence or a mapping cannot be looked up in
            # ``seen``, and PyYAML would refuse it a moment later anyway. The
            # check for a repeated key must not get there first with a
            # ``TypeError``, which is not an error this module can report.
            if not isinstance(key, abc.Hashable):
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found a key that is not a scalar",
                    key_node.start_mark,
                )
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, f"the key {key!r} is repeated", key_node.start_mark
                )
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


# YAML 1.1's implicit resolvers are dropped wholesale: they carry the merge
# key, the timestamp, sexagesimal numbers and the yes/no/on/off booleans. The
# core schema's four are added back in their place.
_Loader.yaml_implicit_resolvers = {}


def _resolve(tag, pattern, first):
    _Loader.add_implicit_resolver(tag, re.compile(pattern, re.X), list(first))


_resolve(
    "tag:yaml.org,2002:null",
    r"^(?: ~ | null | Null | NULL | )$",
    ["~", "n", "N", ""],
)
_resolve(
    "tag:yaml.org,2002:bool",
    r"^(?: true | True | TRUE | false | False | FALSE )$",
    "tTfF",
)
_resolve(
    "tag:yaml.org,2002:int",
    r"^(?: [-+]? [0-9]+ | 0o [0-7]+ | 0x [0-9a-fA-F]+ )$",
    "-+0123456789",
)
_resolve(
    "tag:yaml.org,2002:float",
    r"""^(?: [-+]? (?: \. [0-9]+ | [0-9]+ (?: \. [0-9]* )? ) (?: [eE] [-+]? [0-9]+ )?
           | [-+]? \. (?: inf | Inf | INF )
           | \. (?: nan | NaN | NAN ) )$""",
    "-+0123456789.",
)


def _construct_int(loader, node):
    # The core schema's integers. YAML 1.1 reads a leading zero as octal; here
    # only an explicit 0o is octal, so 010 is ten.
    value = loader.construct_scalar(node)
    if value.startswith("0o"):
        return int(value[2:], 8)
    if value.startswith("0x"):
        return int(value[2:], 16)
    return int(value, 10)


_Loader.add_constructor("tag:yaml.org,2002:int", _construct_int)


def load(text):
    """The document in ``text``, read by the contract's dialect.

    Raises ``Unreadable`` for anything the contract says cannot be read: a
    syntax error, a repeated key, a key that is not a scalar, a second
    document, or an alias.
    """
    try:
        return yaml.load(text, Loader=_Loader)
    except yaml.YAMLError as error:
        raise Unreadable(str(error)) from error
