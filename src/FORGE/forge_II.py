"""
FORGE: PHASE-II module file.

Initializes the matrix generation for the directory deployment.

TODO: [x] Implement an are-you-sure? option.
TODO: [x] Implement the logging function.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from functions_forge import load_blueprint, build_param_dict, generate_combinations, build_deployment_tree
from utils.logging import log

# =================================================================================================

blueprint_name = input('\nPlease, enter the name of the blueprint file, omitting the .json extension, to initialize matrix and .par files generation: ')

file_dict = load_blueprint(blueprint_name)
log('FORGE-II | Blueprint loaded successfully.')

metadata_dict  = file_dict['project_metadata']
paths_dict     = file_dict['paths']
parameter_dict = file_dict['parameters']
setup_name = parameter_dict['Setup']

static_dict, sweep_dict = build_param_dict(parameter_dict)
log('FORGE-II | Dictionaries created successfully.')

run_matrix = generate_combinations(static_dict, sweep_dict)
log('FORGE-II | Matrix calculated successfully.')

while True:
    state = input(f"\nAre you sure you want to write {len(run_matrix)} directories in outputs/? This action will overwrite any existing data and each created directory will contain its respective .par file. (Y/N): ")
    state = state.upper().strip()
    
    if state in ('Y', 'YES'):
        print('\nInitiating deploy...')
        build_deployment_tree(run_matrix, setup_name)
        log(f'FORGE-II | {len(run_matrix)} directories generated in outputs/.')
        print('\nDone!\n')
        break
    
    elif state in ('N', 'NO'):
        print('\nDeployment aborted.\n')
        log('FORGE-II | Aborted module with "exit" option.')
        sys.exit(0)
    
    else:
        print('\nPlease enter a valid answer.\n')