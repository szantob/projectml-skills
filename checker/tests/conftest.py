"""Put the checker's own directory on the path, so tests import its modules
the way the checker itself does when run as a script."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
