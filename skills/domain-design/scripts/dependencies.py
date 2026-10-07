"""Where a script finds the checker, and what it says when it cannot import
what it needs.

Standard library only, so that it can itself always be imported. The
checker says the same thing in the same words; a skill script must not end
instead in a traceback, whose exit status, 1, would read as a verdict on a
package that was never read.
"""

from pathlib import Path

# Where the checker is depends on how the skill arrived. In this repository it
# sits beside skills/, two levels above the skill. In the bundle a claude.ai
# upload takes, it travels inside the skill, because nothing outside the
# skill's own folder is uploaded. The bundle's own copy is looked for first:
# it is the one built from the same commit as the scripts beside it.
SKILL = Path(__file__).resolve().parents[1]
CHECKER = next(
    (
        place
        for place in (SKILL / "checker", SKILL.parents[1] / "checker")
        if place.is_dir()
    ),
    SKILL.parents[1] / "checker",
)
REQUIREMENTS = CHECKER / "requirements.txt"


def explain(error, own_modules):
    """Print why an import failed and return the exit status for it: 2,
    nothing to work from."""
    if error.name in own_modules:
        print(f"The skill is incomplete: {error.name}.py is missing.")
    else:
        print(
            f"This needs PyYAML and jsonschema, and {error.name} is missing. "
            f"Install them with: python -m pip install -r {REQUIREMENTS}"
        )
    return 2
