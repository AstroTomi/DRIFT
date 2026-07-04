"""
VOID: module file.

Wipes out an specified directory.

TODO: [x] Implement an are-you-sure? option.
TODO: [x] Implement the logging function.
"""

import sys, shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.global_variables import CONFIGS_DIR_PATH, LOGS_DIR_PATH, OUTPUTS_DIR_PATH
from utils.logging import log

# =================================================================================================

def purge_directory(target_dir: Path) -> None:
    """### Purges the content of a specified directory

    Args:
        target_dir (_Path_): _Path-object of the directory._
        
    Returns:
        _None_ : _Nothing._
    """
    # Existence verification.
    if not target_dir.exists():
        print(f'  The :{target_dir}/" directory does not exist yet. Nothing to purge.')
        log('VOID | Nothing to purge.')
        return None

    # Purging content.
    deleted_items = 0
    for item in target_dir.iterdir():
        try:
            if item.is_dir():
                # Purges all content on directory.
                shutil.rmtree(item)
                
            else:
                # Purges the file.
                item.unlink()
            
            deleted_items += 1
        
        except Exception as e:
            print(f'  ERROR: Could not delete "{item.name}": {e}')

    # Report messages.
    if deleted_items > 0:
        print(f'  Purged {deleted_items} item(s) from "{target_dir}/".')
        log(f'VOID | Purged {deleted_items} item(s) from {target_dir}.')
        
    else:
        print(f'  The "{target_dir}/" directory is already empty.')
        log('VOID | Nothing purged.')
        
    return None

def main_void():
    """### Main function of VOID module
    """
    args = sys.argv[1:]
    
    if "--configs" in args:
        purge_directory(CONFIGS_DIR_PATH)
        
    elif "--logs" in args:
        purge_directory(LOGS_DIR_PATH)
        
    elif "--outputs" in args:
        purge_directory(OUTPUTS_DIR_PATH)
        
    elif "--all" in args:
        print("  Executing full environment reset...")
        purge_directory(CONFIGS_DIR_PATH)
        purge_directory(LOGS_DIR_PATH)
        purge_directory(OUTPUTS_DIR_PATH)
        
    else:
        # ? This maybe is not necessary.
        print("  ERROR: VOID engine requires specific target flags (--configs, --logs, --outputs or --all).")
        log('VOID ERROR | No flag specified.')
        sys.exit(1)

choice = input('Are you sure you want to perform this action? (Y/N): ')
choice = choice.upper()

while True:
    if choice in ('YES', 'Y'):
        log('VOID | Initiating purge.')
        break
    
    elif choice in ('NO', 'N'):
        log('VOID | Aborted process.')
        sys.exit(0)
        
    else:
        choice = input('\nPlease, enter a valid option (Y/N): ')
        choice = choice.upper()

main_void()