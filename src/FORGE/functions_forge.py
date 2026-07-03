"""
Functions file.

This file contains useful functions for scanning, extracting and constructing data accross FORGE module and FARGO3D.
Do not remove or change this file in any case.
"""

from variables_forge import USER_FARGO_PATH, CONFIG_DIR_PATH, OUTPUT_DIR_PATH
from pathlib import Path
import sys, json, ast, itertools, copy

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
        print(f'CRITICAL ERROR: No setups directory found at {USER_FARGO_PATH}. Exiting.')
        sys.exit(1)

    print('Available setups:')
    print(" | ".join(available_setups) + '\n')

    while True:
        selected_setup = input('Please, select one of the available setups (or type "exit"): ')

        if selected_setup == 'exit':
            print('\nAborting FORGE...')
            sys.exit(0)
        
        elif selected_setup in available_setups:
            print(f'\n[{selected_setup}] setup selected. Generating the main config file...\n')
            par_file_path = USER_FARGO_PATH / 'setups' / f'{selected_setup}' / f'{selected_setup}.par'
            break
        
        else:
            print(f'\nError: "{selected_setup}" is not recognized. Try again.\n')
    
    with open(par_file_path, 'r') as par_file:
        for row in par_file:
            parts = row.split()
            if (len(parts) != 0) and ('#' not in row):
                par_file_parameters.update({parts[0] : parts[1]})
        
        return selected_setup, par_file_parameters

def create_blueprint(setup_name: str, parameters: dict, blueprint_name_external: str) -> None:
    """### Creation of the main config file for the .par files creation
    
    Creates a `.json` file for the main config of the simulations inside the `config/` folder.
    A back-door is implemented in the selection of the blueprint name in order to exit the function.
        
    Args:
        setup_name (_str_): _A string with the selected setup._
        parameters (_dict_): _A dictionary of the found parameters in scanning._
        blueprint_name_external (_str_): _Name of the blueprint selected outside of method._
    Returns:
        _None_: Nothing.
    """
    
    # Auxiliary variables.
    blueprint_path = CONFIG_DIR_PATH / f'{blueprint_name_external}.json'
    blueprint_name = blueprint_name_external
        
    # Checks if file exists.
    while True:
        if blueprint_path.is_file():
            blueprint_name = input('\nA file with that name already exists, please select another (or type "exit"): ')
            
            if blueprint_name == 'exit':
                print('\nAborting FORGE...')
                sys.exit(1)
                
            blueprint_path = CONFIG_DIR_PATH / f'{blueprint_name}.json'
            
        else:
            break
        
    # Content definition.
    blueprint_data = {
        "instructions": [
            "=============================================",
            "FARGO3D: DRIFT - MAIN PARAMETER CONFIGURATION",
            "=============================================",
            "Modify the 'parameters' block below. IGNITE will use these base values.",
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
            "output_directory": f"{OUTPUT_DIR_PATH}/{blueprint_name}_experiments/"
        },
        "parameters": parameters
    }

    # Writing the file with json.dump for automatic pretty-printing.
    try:
        with open(blueprint_path, 'x') as blueprint_file:
            json.dump(blueprint_data, blueprint_file, indent=4)
    
    except FileExistsError:
        print(f'\nERROR: The file {blueprint_name}.json was created by another process.')
        sys.exit(1)
        
    return None

def load_blueprint(blueprint_name: str) -> dict:
    """### Loads the `.json` blueprint file and returns it as a dictionary

    Args:
        blueprint_name (_str_): _Name of the selected blueprint._
        
    Returns:
        _dict_: _A dictionary object containing the items of the `.json` file, this includes information, metadata, paths and parameters, respectively._
    """
    
    blueprint_path = CONFIG_DIR_PATH / f'{blueprint_name}.json'
    
    try:
        with open(blueprint_path, 'r') as blueprint_content:
            return json.load(blueprint_content)
        
    except FileNotFoundError:
        print('\nERROR: The file was not found.')
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




def build_deployment_tree(matrix: list[dict], output_dir: str, setup_name: str) -> None:
    """
    Iterates over the generated matrix, creates the run_X folders, 
    and writes the specific .par files for FARGO3D.
    """
    base_dir = Path(output_dir)
    # Create the main experiments directory if it doesn't exist
    base_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[GENESIS] Deploying {len(matrix)} configurations in {base_dir.name}/...")

    for i, sim_params in enumerate(matrix, start=1):
        # 1. Create the individual run folder (run_1, run_2, ...)
        run_folder = base_dir / f"run_{i}"
        run_folder.mkdir(exist_ok=True)
        
        # 2. Define the path for the new .par file
        par_file_path = run_folder / f"{setup_name}.par"
        
        # 3. Write the physics configuration file
        with open(par_file_path, 'w') as par_file:
            par_file.write(f"# FARGO3D: DRIFT - SIMULATION RUN {i}\n")
            par_file.write(f"# ==========================================\n")
            
            for key, value in sim_params.items():
                # The :<20 formatting aligns the columns nicely for human readability
                par_file.write(f"{key:<20} {value}\n")
                
        print(f"  + Folder ready: {run_folder.name}/")