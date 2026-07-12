import sys, subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from functions_launch import extract_setup_name
from utils.global_variables import USER_FARGO_PATH
from utils.logging import log

# =================================================================================================

setup_name = extract_setup_name()

gpu_flag = 0
parallel_flag = 0

# Cleaning of bin/ directory.
subprocess.run(["make", "mrproper"], cwd = USER_FARGO_PATH)

# Setup definition.
subprocess.run(
    [
        "make",
        f"SETUP={setup_name}",
        f"GPU={gpu_flag}",
        f"PARALLEL={parallel_flag}",
    ],
    cwd = USER_FARGO_PATH
    )