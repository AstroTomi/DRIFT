import sys, json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from utils.global_variables import CONFIGS_DIR_PATH
from utils.logging import log

# =================================================================================================

def extract_setup_name():
    # Auxiliary variable
    available_config_files = []

    # Config file searcher
    if CONFIGS_DIR_PATH.is_dir():
        print('\nConfigurations directory found!, scanning for available configuration files...\n')

        for item in CONFIGS_DIR_PATH.iterdir():
                if item.is_file() and item.suffix == '.json':
                    available_config_files.append(item.stem)

        if not available_config_files:
            print(f'CRITICAL ERROR: No configuration file found at {CONFIGS_DIR_PATH}. Exiting...\n')
            log(f'LAUNCH-I CRITICAL ERROR | No configuration file found at {CONFIGS_DIR_PATH}.')
            sys.exit(1)

    else:
        print(f'CRITICAL ERROR: No configurations directory found at {CONFIGS_DIR_PATH}. Exiting...\n')
        log(f'LAUNCH-I CRITICAL ERROR | No configurations directory found at {CONFIGS_DIR_PATH}.')
        sys.exit(1)


    print('Available configuration files:')
    print(" | ".join(available_config_files) + '\n')

    config_file_name = input('Please, select one of the available configuration files in order to initialize the simulations: ')

    config_file_path = CONFIGS_DIR_PATH / f'{config_file_name}.json'

    # Error handler.
    try:
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            _cfg = json.load(config_file)
        setup_name = _cfg['parameters']['Setup']
        log(f'LAUNCH-I | Selected setup: {setup_name}.')

    except FileNotFoundError:
        print(f"\nCRITICAL ERROR: Configuration file not found at: {CONFIGS_DIR_PATH}")
        print(F"Please ensure '{config_file_name}.json' exists inside the configs/ directory.\n", file = sys.stderr)
        log(f'LAUNCH-I CRITICAL ERROR | No configuration file found at {CONFIGS_DIR_PATH}.')
        sys.exit(1)

    except KeyError:
        print(f"\nCRITICAL ERROR: Setup parameter not found at: {config_file_path}")
        print(F"Please ensure 'Setup' parameter exists inside the '{config_file_name}.json' file.\n", file = sys.stderr)
        log(f"LAUNCH-I CRITICAL ERROR | No 'Setup' parameter found at '{config_file_name}.json' file.")
        sys.exit(1)

    return setup_name