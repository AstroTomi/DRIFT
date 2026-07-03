"""
FORGE: PHASE-I module file.

Initializes the setup selector and blueprint generator.
"""

from functions_forge import run_scan_and_selection, create_blueprint

selected_setup, parameters_dict = run_scan_and_selection()

blueprint_name = input('Please, enter a name for the blueprint file, omitting the file extension: ')

create_blueprint(selected_setup, parameters_dict, blueprint_name)

print("""\nDone!\n
Please proceed with the configuration of the blueprint file on config/ folder, it will contain the selected name.\n
Then, run the following command on the root directory in order to initialize the variables and create the multiple .par files.\n
      "./drift forge -c"    or    "./drift forge --calculate"
""")