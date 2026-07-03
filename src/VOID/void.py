import sys
import shutil
from pathlib import Path

from variables_void import CONFIG_DIR_PATH, LOGS_DIR_PATH, OUTPUTS_DIR_PATH

def purge_directory(target_dir: Path) -> None:
    """### Purges the content of a specified directory.

    Args:
        target_dir (_Path_): _Path-object of the directory._
        
    Returns:
        _None_ : _Nothing._
    """
    # Existence verification.
    if not target_dir.exists():
        print(f'  The :{target_dir}/" directory does not exist yet. Nothing to purge.')
        
        return

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
    else:
        print(f'  The "{target_dir}/" directory is already empty.')

def main_void():
    args = sys.argv[1:]
    
    if "--config" in args:
        purge_directory(CONFIG_DIR_PATH)
        
    elif "--logs" in args:
        purge_directory(LOGS_DIR_PATH)
        
    elif "--outputs" in args:
        purge_directory(OUTPUTS_DIR_PATH)
        
    elif "--all" in args:
        print("  Executing full environment reset...")
        purge_directory(CONFIG_DIR_PATH)
        purge_directory(LOGS_DIR_PATH)
        purge_directory(OUTPUTS_DIR_PATH)
        
    else:
        print("  ERROR: VOID engine requires specific target flags (--config, --logs, --outputs or --all).")
        sys.exit(1)

if __name__ == "__main__":
    main_void()