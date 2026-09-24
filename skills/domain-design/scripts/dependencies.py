"""What a script says when it cannot import what it needs.

Standard library only, so that it can itself always be imported. The
checker says the same thing in the same words; a skill script must not end
instead in a traceback, whose exit status, 1, would read as a verdict on a
package that was never read.
"""

from pathlib import Path

CHECKER = Path(__file__).resolve().parents[3] / "checker"
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
