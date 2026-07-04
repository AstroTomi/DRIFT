"""
Functions file.

This file contains useful functions for scanning, extracting and constructing data accross FORGE module and FARGO3D.
Do not remove or change this file in any case.

TODO: [x] Finish the deployment_tree() function.
TODO: [x] Make sure that create_blueprint creates configs/ directory.
TODO: [x] Implement the logging function.
"""

import sys, json, ast, itertools, copy, shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.global_variables import USER_FARGO_PATH, CONFIGS_DIR_PATH, OUTPUTS_DIR_PATH
from utils.logging import log

# ============================================ FORGE-I ============================================

def run_scan_and_selection() -> tuple[str, dict]:
    """### Scan and selection of the setup
    
    1. Verification of the existence of setups directory.
    2. Show available setups.
    3. Wait for the input of the desired setup.
    4. Scanning of the parameters on the `.par` file.
    5. Storing the parameters and original values on a dict object.
    
    If no setups directory or setup is found the program terminates.
    A back-door is implemented in the selection of the setup in order to exit the function.

    Returns:
        _tuple_: _A tuple containing a string with the selected setup and a dictionary of the found parameters, respectively._
    """
    
    # Auxiliary variables.
    setups_path = USER_FARGO_PATH / 'setups'
    available_setups = []
    par_file_parameters = {}
    
    print('\nScanning for setups directory...\n')

    if setups_path.is_dir():
        print('Setups directory found!, scanning for available setups...\n')
        
        for item in setups_path.iterdir():
            if item.is_dir():
                available_setups.append(item.name)

    else:
        print(f'CRITICAL ERROR: No setups directory found at {USER_FARGO_PATH}. Exiting...\n')
        log(f'FORGE-I CRITICAL ERROR | No setups directory found at {USER_FARGO_PATH}.')
        sys.exit(1)

    print('Available setups:')
    print(" | ".join(available_setups) + '\n')

    while True:
        selected_setup = input('Please, select one of the available setups (or type "exit"): ').strip()

        if selected_setup == 'exit':
            print('\nAborting FORGE...\n')
            log('FORGE-I | Aborted module with "exit" option.')
            sys.exit(0)
        
        elif selected_setup in available_setups:
            print(f'\n[{selected_setup}] setup selected. Generating the main blueprint file...\n')
            par_file_path = USER_FARGO_PATH / 'setups' / f'{selected_setup}' / f'{selected_setup}.par'
            break
        
        else:
            print(f'\nError: "{selected_setup}" is not recognized. Try again.\n')
    
    with open(par_file_path, 'r', encoding = 'utf-8') as par_file:
        for row in par_file:
            parts = row.split()
            if (len(parts) != 0) and ('#' not in row):
                par_file_parameters.update({parts[0] : parts[1]})
        
        return selected_setup, par_file_parameters

def create_blueprint(setup_name: str, parameters: dict, blueprint_name_external: str) -> str:
    """### Creation of the main blueprint file for the .par files creation
    
    Creates a `.json` file for the main config of the simulations inside the `configs/` folder.
    A back-door is implemented in the selection of the blueprint name in order to exit the function.
        
    Args:
        setup_name (_str_): _A string with the selected setup._
        parameters (_dict_): _A dictionary of the found parameters in scanning._
        blueprint_name_external (_str_): _Name of the blueprint selected outside of method._
    Returns:
        _str_: _A string with the name of the blueprint._
    """
    
    # Making sure that configs/ exists.
    CONFIGS_DIR_PATH.mkdir(parents = True, exist_ok = True)
    
    # Auxiliary variables.
    blueprint_path = CONFIGS_DIR_PATH / f'{blueprint_name_external}.json'
    blueprint_name = blueprint_name_external
        
    # Checks if file exists.
    while True:
        if blueprint_path.is_file():
            choice = input('\nA file with that name already exists, do you want to overwrite it? (Y/N, or type "exit"): ')
            choice = choice.strip().upper()
            
            if choice == 'EXIT':
                print('\nAborting FORGE...\n')
                log('FORGE-I | Aborted module with "exit" option.')
                sys.exit(1)
                
            elif choice.upper() in ('YES', 'Y'):
                blueprint_path.unlink()
                log(f'FORGE-I | The "{blueprint_name}.json" file has been overwritten.')
                break
            
            elif choice.upper() in ('NO', 'N'):
                blueprint_name = input('\nPlease select another name: ').strip()
                blueprint_path = CONFIGS_DIR_PATH / f'{blueprint_name}.json'
        
        else:
            # If not same name, continue.
            break
        
    # Content definition.
    blueprint_data = {
        "instructions": [
            "=============================================",
            "FARGO3D: DRIFT - MAIN PARAMETER CONFIGURATION",
            "=============================================",
            "Modify the 'parameters' block below. LAUNCH will use these base values.",
            "If you define a parameter as a list (e.g., [value1, value2]),",
            "the program will generate a cartesian product of the possible values."
        ],
        "project_metadata": {
            "project_name": f"Parameter Sweep on the {setup_name} setup",
            "author": "Author name",
            "description": "A brief description of the project."
        },
        "paths": {
            "base_par_file": f"setups/{setup_name}/{setup_name}.par",
            "output_directory": f"{OUTPUTS_DIR_PATH}/"
        },
        "parameters": parameters
    }

    # Writing the file with json.dump for automatic pretty-printing.
    try:
        with open(blueprint_path, 'x', encoding = 'utf-8') as blueprint_file:
            json.dump(blueprint_data, blueprint_file, indent=4)
    
    except FileExistsError:
        print(f'\nERROR: The file {blueprint_name}.json was created by another process.')
        log(f'FORGE-I ERROR | The file {blueprint_name}.json was created by another process.')
        sys.exit(1)
        
    return blueprint_name

# ============================================ FORGE-II ===========================================

def load_blueprint(blueprint_name: str) -> dict:
    """### Loads the `.json` blueprint file and returns it as a dictionary

    Args:
        blueprint_name (_str_): _Name of the selected blueprint._
        
    Returns:
        _dict_: _A dictionary object containing the items of the `.json` file, this includes information, metadata, paths and parameters, respectively._
    """
    
    blueprint_path = CONFIGS_DIR_PATH / f'{blueprint_name}.json'
    
    try:
        with open(blueprint_path, 'r', encoding = 'utf-8') as blueprint_content:
            return json.load(blueprint_content)
        
    except FileNotFoundError:
        print(f'\nERROR: The file "{blueprint_name}.json" was not found.\n')
        log(f'FORGE-II ERROR | The file "{blueprint_name}.json" was not found.')
        sys.exit(1)

def build_param_dict(parameter_dict: dict) -> tuple[dict, dict]:
    """### Dictionary builder
    
    Takes the parameter dictionary from the `.json` file and builds the sweep and static parameter dictionaries

    Args:
        parameter_dict (dict): _A dictionary containing the parameters defined in the `.json` blueprint file._

    Returns:
        _tuple_: _A tuple containing the static and sweep parameter dictionaries, respectively._
    """
    
    # Auxiliary variables.
    static_params = {}
    sweep_params = {}

    for key, value in parameter_dict.items():
        # Auxiliary variable.
        parsed_value = value
        
        # Checks if a value can be converted into a list.
        if isinstance(value, str):
            val_stripped = value.strip()
            if val_stripped.startswith('[') and val_stripped.endswith(']'):
                try:
                    # Transforms into a native list.
                    parsed_value = ast.literal_eval(val_stripped)
                
                except ValueError:
                    pass
            
            else:
                try:
                    if '.' in val_stripped or 'e' in val_stripped.lower():
                        # Transforms into a native float.
                        parsed_value = float(val_stripped)
                        
                    else:
                        # Transforms into a native int.
                        parsed_value = int(val_stripped)
                            
                except ValueError:
                    pass
        
        # Classification.
        if isinstance(parsed_value, list):
            sweep_params[key] = parsed_value
        
        else:
            static_params[key] = parsed_value
        
    return static_params, sweep_params

def generate_combinations(static_params: dict, sweep_params: dict) -> list[dict]:
    """_Generates a list containing all possible parameter combinations as dictionaries._

    Note on Memory Management:
    Python variables are names bound to object references. To prevent nested structures from sharing memory space and overwriting previous run configurations, copy.deepcopy() is explicitly used for every combination.

    Args:
        static_params (dict): _Dictionary of static parameters._
        sweep_params (dict): _Dictionary of non-static parameters._

    Returns:
        list[dict]: _A list containing all possible configurations of parameters as dictionaries._
    """
    # If no lists are found, return a single configuration. This is, a single simulation.
    if not sweep_params:
        return [static_params]

    # Auxiliary variable.
    run_matrix = []

    # Sweep vectors.
    sweep_keys = list(sweep_params.keys())
    sweep_values = list(sweep_params.values())

    # Cartesian product between sweep vectors.
    # The asterisk (*) unpacks the list of lists so itertools can cross them.
    combinations = list(itertools.product(*sweep_values))

    # Building of the parameter matrix.
    for pack in combinations:
        # Deepcopy is required because Python variables act as memory references, not independent containers.
        sim_params = copy.deepcopy(static_params)
        
        # Inject the specific values for this combination iteration
        for i, key in enumerate(sweep_keys):
            sim_params[key] = pack[i]
            
        run_matrix.append(sim_params)

    return run_matrix

def build_deployment_tree(run_matrix: list[dict], setup_name: str) -> None:
    """### Main deploy of directories and `.par` files
    
    _Generates directories based on the number of simulations given by the matrix, each one with its own `.par` file._

    Args:
        run_matrix (_list[dict]_): _A list containing all possible configurations of parameters as dictionaries._
        setup_name (_str_): _A string with the selected setup._

    Returns:
        _None_: _Nothing._
    """
    # Auxiliary variables.
    total_runs = len(run_matrix)
    pad_width = max(3, len(str(total_runs)))

    par_file_path = USER_FARGO_PATH / 'setups' / setup_name / f'{setup_name}.par'
    par_file_rows = []

    # Copy of the data from the original base .par file.
    with open(par_file_path, 'r', encoding = 'utf-8') as par_file_content:
        for row in par_file_content:
            par_file_rows.append(row)

    for run in range(1, total_runs + 1):
        
        ## First block: Creating directories.
        
        # Directory creation.
        run_name = f"run_{run:0{pad_width}d}"
        run_dir = OUTPUTS_DIR_PATH / run_name
        
        # if directory exists, it is purged.
        if run_dir.exists():
            log(f'FORGE-II | Overwriting existing run directory: {run_name}')
            shutil.rmtree(run_dir)
        
        run_dir.mkdir(parents = True, exist_ok = True)
        
        ## Second block: Creating .par files.
        
        # Dictionary of replacements for this specific run.
        current_run_params = run_matrix[run - 1].copy()
        
        # OutputDir pointing to the isolated run folder.
        current_run_params['OutputDir'] = f"{run_dir.resolve()}/"
        
        # This is for tracking the keys that have been replaced in place.
        replaced_keys = set()
        new_par_rows = []

        for row in par_file_rows:
            # Auxiliary variable.
            stripped_row = row.strip()
            
            # A row is ignored if it's empy or is a comment.
            if not stripped_row or stripped_row.startswith('#'):
                new_par_rows.append(row)
                continue
                
            split_row = stripped_row.split()
            # The parameter name is always the first word.
            key = split_row[0]
            
            # Check if this row's key needs to be overwritten.
            if key in current_run_params:
                value = current_run_params[key]
                # Key aligned to 30 chars, then the value.
                new_row = f"{key:<30}\t{value}\n"
                new_par_rows.append(new_row)
                replaced_keys.add(key)
                
            else:
                # Keep the original line intact.
                new_par_rows.append(row)
                
        # Sanity check: if there are any parameters in current_run_params that were NOT 
        # in the original .par file, append them at the end so they aren't lost.
        missing_keys = set(current_run_params.keys()) - replaced_keys
        if missing_keys:
            new_par_rows.append("\n### DRIFT INJECTED PARAMETERS ###\n")
            for key in sorted(missing_keys):
                new_par_rows.append(f"{key:<30}\t{current_run_params[key]}\n")

        # Write .par file directly inside outputs/run_XXX/
        destination_par = run_dir / f"{setup_name}.par"
        try:
            with open(destination_par, 'x', encoding = 'utf-8') as out_file:
                out_file.writelines(new_par_rows)

        except FileExistsError:
            # Write to log with time and file name / directory.
            log(f'FORGE-II ERROR | Setup file ".par" exists at {run_dir}.')
            continue
    
    return None