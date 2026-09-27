import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills' / 'docs-for-humans'
SCRIPTS = SKILL / 'scripts'
EXAMPLES = ROOT / 'examples' / 'docs-for-humans'

sys.path.insert(0, str(SCRIPTS))
