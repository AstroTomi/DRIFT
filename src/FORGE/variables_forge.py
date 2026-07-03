"""
Variables file.

This file contains all the static variables that are used un FORGE module.
You should only change the USER_FARGO_PATH variable in order to conect with the root folder of FARGO3D.
Do not remove or change this file in any other case.
"""

from pathlib import Path

USER_FARGO_PATH = Path('/home/astrotomi/Documents/local/fargo3d')

ROOT_DIR = Path(__file__).parents[2]
CONFIG_DIR_PATH = ROOT_DIR / 'config'
OUTPUT_DIR_PATH = ROOT_DIR / 'outputs'