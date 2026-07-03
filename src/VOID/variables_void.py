"""
Variables file.

This file contains all the static variables that are used un VOID module.
Do not remove or change this file in any other case.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).parents[2]
CONFIG_DIR_PATH = ROOT_DIR / 'config'
LOGS_DIR_PATH   = ROOT_DIR / 'logs'
OUTPUTS_DIR_PATH = ROOT_DIR / 'outputs'