"""Put the checker and the skill's own scripts on the path, the way the
script does when it is run directly."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent.parent.parent / "checker"))
