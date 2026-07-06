"""
FORGE: PHASE-I module file.

Initializes the setup selector and blueprint generator.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from functions_forge import run_scan_and_selection, create_blueprint
from utils.logging import log

# =================================================================================================

selected_setup, parameters_dict = run_scan_and_selection()
log('FORGE-I | Scan and setup selection completed successfully.')

blueprint_name = input('Please, enter a name for the blueprint file, omitting the file extension: ').strip()
blueprint_official_name = create_blueprint(selected_setup, parameters_dict, blueprint_name).strip()
log(f'FORGE-I | Blueprint "{blueprint_official_name}".json creation completed successfully.')

print("""\nDone!\n
Please proceed with the configuration of the blueprint file on config/ folder, it will contain the selected name.\n
Then, run the following command on the root directory in order to initialize the variables and create the multiple .par files.\n
      "./drift forge -d"    or    "./drift forge --deploy"
""")
log(f'FORGE-I | Module has finished completely.')