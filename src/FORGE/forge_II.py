"""
FORGE: PHASE-II module file.

Initializes the matrix generation for the directory deployment..
"""

from functions_forge import load_blueprint, build_param_dict, generate_combinations

blueprint_name = input('\nPlease, enter the name of the blueprint file, omitting the .json extension, to initialize matrix and .par files generation: ')

file_dict = load_blueprint(blueprint_name)

metadata_dict  = file_dict['project_metadata']
paths_dict     = file_dict['paths']
parameter_dict = file_dict['parameters']

static_dict, sweep_dict = build_param_dict(parameter_dict)

run_matrix = generate_combinations(static_dict, sweep_dict)