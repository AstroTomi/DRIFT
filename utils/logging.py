"""
Logging file.

This file contains the function needed to log utility messages to logs/. It is used across all DRIFT.

TODO: [x] Change file extension from .txt lo .log
"""

from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.global_variables import ROOT_DIR, LOGGING_ENABLED

# =================================================================================================

def log(message: str) -> None:
    """### Logging function
    
    _Writes a specified message on logs/, dynamically indicating the date on the .txt file and the time inside it._
    _If LOGGING_ENABLED is set to False, the function does nothing._
    
    Args:
        message (_str_): _The specified message to be written to logs/._
        
    Returns:
        _None_: Nothing.
    """
    
    if not LOGGING_ENABLED:
        return None

    # Timestamps.
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Making sure that logs/ exists.
    logs_dir = ROOT_DIR / "logs"
    logs_dir.mkdir(parents = True, exist_ok = True)

    # Creating the log file.
    log_file = logs_dir / f"log_{date_str}.log"

    # This is the line to be written.
    formatted_line = f"[{time_str}]: {message}\n"

    try:
        with open(log_file, 'a' , encoding = 'utf-8') as file:
            file.write(formatted_line)
            
    except Exception as e:
        print(f"  WARNING: DRIFT could not write to log: {e}", file = sys.stderr)
        
    return None