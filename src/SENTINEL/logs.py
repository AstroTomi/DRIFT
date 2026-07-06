import sys, json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.global_variables import DRIFT_CONFIG_PATH
import utils.logging as lg

# =================================================================================================

def main_toggle_log():
    """### Main toggle logging file.
    """
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
    
    args = sys.argv[1:]
    state = _cfg["telemetry"]["logging_enabled"]
    
    if "--enablelogs" in args:
        if state == True:
            print('Log writting is already enabled.')
            return None
        
        _cfg["telemetry"]["logging_enabled"] = True
        with open(DRIFT_CONFIG_PATH, 'w', encoding = 'utf-8') as config_file:
            json.dump(_cfg, config_file, indent = 4)
        print('Log writting has been enabled.')
        lg.LOGGING_ENABLED = True
        lg.log("SENTINEL | Log writting has been enabled.")
    
    elif "--disablelogs" in args:
        if state == False:
            print('Log writting is already disabled.')
            return None
        
        lg.log("SENTINEL | Log writting has been disabled.")
        _cfg["telemetry"]["logging_enabled"] = False
        with open(DRIFT_CONFIG_PATH, 'w', encoding = 'utf-8') as config_file:
            json.dump(_cfg, config_file, indent = 4)
        print('Log writting have been disabled.')
        
    elif "--status" in args:
        if state == True:
            state = "ENABLED"
            
        else:
            state = "DISABLED"
            
        print(f'Current log status: {state}.')
    
    else:
        print("  ERROR: SENTINEL engine requires specific target flags (--enablelogs, --logs, --outputs or --all).\n")
        lg.log('SENTINEL ERROR | No flag specified.')
        sys.exit(1)
    
    return None

main_toggle_log()