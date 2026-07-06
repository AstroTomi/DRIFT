"""
Variables file.

This file contains all the static variables that are used across DRIFT.
Do not remove or change this file in any other case.
"""

import json, sys
from pathlib import Path

# =================================================================================================

# Main root directory.
ROOT_DIR = Path(__file__).parents[1]

# Some useful directories.
CONFIGS_DIR_PATH = ROOT_DIR / 'configs'
OUTPUTS_DIR_PATH = ROOT_DIR / 'outputs'
LOGS_DIR_PATH   = ROOT_DIR / 'logs'

# Configuration file path.
DRIFT_CONFIG_PATH = Path(__file__).parent / 'drift_config.json'

# Error handler.
try:
    with open(DRIFT_CONFIG_PATH, 'r', encoding='utf-8') as config_file:
        _cfg = json.load(config_file)

except FileNotFoundError:
    print(f"\nCRITICAL ERROR: Configuration file not found at: {DRIFT_CONFIG_PATH}")
    print("Please ensure 'drift_config.json' exists inside the utils/ directory.\n", file=sys.stderr)
    sys.exit(1)

except json.JSONDecodeError as e:
    print(f"\nCRITICAL ERROR: Syntax error in {DRIFT_CONFIG_PATH}: {e}\n", file=sys.stderr)
    sys.exit(1)

USER_FARGO_PATH     = Path(_cfg["environment"]["fargo3d_path"])
LOGGING_ENABLED     = _cfg["telemetry"]["logging_enabled"]