import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ETL_PATH = PROJECT_ROOT / "src" / "etl"

if str(ETL_PATH) not in sys.path:
    sys.path.insert(0, str(ETL_PATH))