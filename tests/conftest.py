"""Make `import agentkit` work regardless of install state or cwd."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
