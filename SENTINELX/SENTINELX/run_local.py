"""Run SENTINELX locally with one command: python run_local.py"""

from pathlib import Path
import sys

import uvicorn


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root))
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
