# define the coomand line inputs and parse them
import argparse
from html import parser
import numpy as np
import os
import pandas as pd
import requests
import sys

import query

####################
# Defining constants
USAGE_ERROR_MESSAGE = '''\nUsage: python main.py <planet_id> OR <planet_ID_list_filename> plus optional flags (see below)
Example: python main.py Gaia DR3 12345678 OR python main.py planet_ids.txt --dr5
Accepted file formats are .txt and .csv
IDs are the whole ID and should include the acronym of the catalog. I.e. Gaia DR3 123456789 or TIC 123456
If you only have the number values of the IDs, add the appropriate flag to the end to specify the catalogue.
e.g. python main.py 123456789 --hd or python main.py planet_ids.csv --tic
Optional flags:
    --gaiadr3  : Lookup based on Gaia DR3 catalog ID
    --tic      : Lookup based on TIC catalog ID
    --hipp     : Lookup based on Hipparcos catalog ID
    --hd       : Lookup based on Henry Draper catalog ID
    --multi_cat: Indicates multiple catalogues are provided in the input file
    --dr5      : Calculate based on DR5 observaton timeline (DR4 is default)
    --load_file: Load a previous query result from a .npy file instead of querying again
'''
####################

def interpret_user_input():
    # Variable that tracks the catalogue ID type
    cat_id_type = None

    if len(sys.argv) < 2:
        print("ERROR: Not enough arguments provided.")
        print(USAGE_ERROR_MESSAGE)
        sys.exit(1)
    
     # Check if the first argument is a file
    
    if sys.argv[1].endswith('.txt') or sys.argv[1].endswith('.csv'):
        # Records if the file is a .txt or a .csv (used for parsing purposes later)
        file_extension = os.path.splitext(sys.argv[1])[1]
        print(f"File extension detected: {file_extension}")
        file_path = sys.argv[1]
        
        # Sets the catalogue ID type to the file extension initially (for later use)
        cat_id_type = file_extension
        
        # If there is no file, throw an error and exit
        if not os.path.isfile(file_path):
            print(f"ERROR: File not found: {file_path}")
            print(USAGE_ERROR_MESSAGE)
            sys.exit(1)
        
        # Parse the file to get the planet IDs and set the cat_id_type
        planet_ids_df = pd.read_csv(file_path, names=['ID'], header=None, comment='#', skip_blank_lines=True)
        print("PLANET IDS DF FROM FILE: \n", planet_ids_df)
        print(planet_ids_df.info())

        print("datatype of [0] entry: ", type(planet_ids_df.iloc[0,0]))
        
        print("BEFORE ADDING CAT ID TYPE: \n", planet_ids_df)
        planet_ids_df["cat_id_type"] = "Unknown"
        print("AFTER SETTING CAT ID TYPE COLUMN TO UNKNOWN: \n", planet_ids_df)
        planet_ids_df.loc[planet_ids_df["ID"].str.startswith("Gaia DR3"), "cat_id_type"] = "gaia_dr3_id"
        planet_ids_df.loc[planet_ids_df["ID"].str.startswith("TIC"), "cat_id_type"] = "tic_id"
        planet_ids_df.loc[planet_ids_df["ID"].str.startswith("HIP"), "cat_id_type"] = "hip_name"
        planet_ids_df.loc[planet_ids_df["ID"].str.startswith("HD"), "cat_id_type"] = "hd_name"

        print("AFTER ADDING CAT ID TYPE: \n", planet_ids_df)
            
        print(f"Read {len(planet_ids_df)} planet IDs from file {file_path}")
        # print(planet_ids)
    
    # If there is no file extension found, assume direct input of one planet ID
    else:
        cat_id_type = 'single'

        # Create a dartaframe that holds the single planet ID and its catalogue type
        planet_ids_df = pd.DataFrame()

        # Check what type of ID is being input based on the the user input
        # If a full ID is given, look for the catalogue acronym in the input
        try:
            if sys.argv[1] == "Gaia" and sys.argv[2] == "DR3":
                int(sys.argv[3])
                # add a row to the dataframe with the planet ID and cat_id_type
                planet_ids_df = pd.DataFrame({'ID': ['Gaia DR3 ' + sys.argv[3]], 'cat_id_type': ['gaia_dr3_id']})
                print("PLANET IDS DF FROM DIRECT INPUT: \n", planet_ids_df)
                # planet_ids = sys.argv[3]
                # cat_id_type = 'gaia_dr3_id'
            elif sys.argv[1] == "TIC":
                int(sys.argv[2])
                planet_ids_df = pd.DataFrame({'ID': ['TIC ' + sys.argv[2]], 'cat_id_type': ['tic_id']})
                print("PLANET IDS DF FROM DIRECT INPUT: \n", planet_ids_df)
                # planet_ids = sys.argv[2]
                # cat_id_type = 'tic_id'
            elif sys.argv[1] == "HIP":
                int(sys.argv[2])
                planet_ids_df = pd.DataFrame({'ID': ['HIP ' + sys.argv[2]], 'cat_id_type': ['hip_name']})
                print("PLANET IDS DF FROM DIRECT INPUT: \n", planet_ids_df)
                # planet_ids = sys.argv[2]
                # cat_id_type = 'hip_name'
            elif sys.argv[1] == "HD":
                int(sys.argv[2])
                planet_ids_df = pd.DataFrame({'ID': ['HD ' + sys.argv[2]], 'cat_id_type': ['hd_name']})
                print("PLANET IDS DF FROM DIRECT INPUT: \n", planet_ids_df)
                # planet_ids = sys.argv[2]
                # cat_id_type = 'hd_name'
            
            # If only a single integer is given, assume it's just the number part of an ID and the user will specify the catalogue with a flag
            elif isinstance(int(sys.argv[1]),int):
                if len(sys.argv) < 3:
                    raise ValueError("Not enough arguments provided")
                int(sys.argv[1])
                planet_ids_df = pd.DataFrame({'ID': [sys.argv[1]], 'cat_id_type': None})
                print("PLANET IDS DF: ", planet_ids_df)
            else:
                raise ValueError("Invalid input format")
        except ValueError:
            print("INPUT ERROR")
            print(USAGE_ERROR_MESSAGE)
            sys.exit(1)
    return planet_ids_df, cat_id_type

# Main execution
if __name__ == "__main__":

    # Create an argument parser and define the expected and possible arguments
    parser = argparse.ArgumentParser()
    
    # The only mandatory argument is the planet ID or the file containing the planet IDs (but a flag should be used if no full ID is given)
    parser.add_argument('planet_ids', nargs='*')

    # Optional flags that specify the catalogue type
    parser.add_argument('--gaiadr3', '--GAIADR3', '--GaiaDR3', action='store_true')
    parser.add_argument('--tic', '--TIC', '--Tic', action='store_true')
    parser.add_argument('--hipp', '--HIPP', '--Hipp', '--HIPPARCOS', '--Hipparcos', '--hipparcos', '--hip', '--HIP', '--Hip', action='store_true')
    parser.add_argument('--hd', '--HD', '--Hd', action='store_true')
    # this argument specifies that multiple catalogues are provided in the input file
    parser.add_argument('--multi_cat', '--MULTI_CAT', '--Multi_Cat', '--multicat', '--MULTICAT', '--MultiCat', action='store_true')
    
    # Optional flag that specifies using DR5 observation timeline
    parser.add_argument('--dr5', '--DR5', '--Dr5', action='store_true')

    parser.add_argument('--load_file', '--LOAD_FILE', '--Load_File')

    # Collect the parsed arguments
    args = parser.parse_args()

    # Prints out the args for debugging purposes
    print("Arguments parsed:")
    print("Gaia:", args.gaiadr3)
    print("TIC:", args.tic)
    print("Hipparcos:", args.hipp)
    print("Henry Draper:", args.hd)
    print("Multiple Categories: ", args.multi_cat)
    print("DR5:", args.dr5)
    print("Load file:", args.load_file)
    print("")

    # If the user has specified to load a previous query result from a .npy file, load
    #   the file instead of querying
    if args.load_file:
        print("Loading previous query result from file: ", args.load_file)
        # Load the previous query result from a .npy file
        try:
            loaded_data = np.load("exoplanet_query_results.npy", allow_pickle=True)
            query_result_df = pd.DataFrame(loaded_data.tolist())
            print("Loaded query result from exoplanet_query_results.npy:")
            print(query_result_df)
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)

    # Interpret the command line arguments to obtain planet IDs and the catalogue ID type
    else:
        planet_ids, cat_id_type = interpret_user_input()

        # If the user fed in a single planet ID without the catalogue acronym, determine the catalogue type from the flags
        try:
            if planet_ids['cat_id_type'].iloc[0] is None:
                if args.gaiadr3:
                    cat_id_type = 'gaia_dr3_id'
                    planet_ids['ID'] = 'Gaia DR3 ' +planet_ids['ID'].astype(str)
                    planet_ids['cat_id_type'] = 'gaia_dr3_id'
                elif args.tic:
                    cat_id_type = 'tic_id'
                    planet_ids['ID'] = 'TIC ' + planet_ids['ID'].astype(str)
                    planet_ids['cat_id_type'] = 'tic_id'
                elif args.hipp:
                    cat_id_type = 'hip_name'
                    planet_ids['ID'] = 'HIP ' + planet_ids['ID'].astype(str)
                    planet_ids['cat_id_type'] = 'hip_name'
                elif args.hd:
                    cat_id_type = 'hd_name'
                    planet_ids['ID'] = 'HD ' + planet_ids['ID'].astype(str)
                    planet_ids['cat_id_type'] = 'hd_name'
                else:
                    raise ValueError("No catalogue type specified")
        except ValueError:
            print("Error determining ID type. Please ensure you provide a valid ID or use the appropriate flag.")
            print(USAGE_ERROR_MESSAGE)
            sys.exit(1)
        
        # CHANGE THE LIST OF PLANET IDS TO BE A COLUMN IN A DATA FRAME; ADD A COLUMN FOR cat_id_type
        # - Used for situations where multiple catalogues are provided in the input file or
        #   if a user has failed to specify the catalogue type for a file input
    
        # Check if there is a flag is set for the input file type
        if cat_id_type == '.csv' or cat_id_type == '.txt':
            if args.multi_cat:
                cat_id_type = 'multi_cat'
            elif args.gaiadr3:
                cat_id_type = 'gaia_dr3_id'
            elif args.tic:
                cat_id_type = 'tic_id'
            elif args.hipp:
                cat_id_type = 'hip_name'
            elif args.hd:
                cat_id_type = 'hd_name'
            else:
                print("No catalogue type flag provided for file input. Assuming multiple catalogues are provided.")
                cat_id_type = 'multi_cat'
            
            print(f"Using ID type: {cat_id_type}")

            # returned_query = query.exoplanet_query(planet_ids, cat_id_type=cat_id_type, data_release='DR5' if args.dr5 else 'DR4')

        # else:
        #     # Can immediately call the query with the single planet ID and the cat_id_type

        #     returned_query = query.exoplanet_query(planet_ids, cat_id_type=cat_id_type, data_release='DR5' if args.dr5 else 'DR4')

        print("FINAL PLANET IDS DF TO BE USED IN QUERY: \n", planet_ids)

        returned_query = query.exoplanet_query(planet_ids, data_release='DR5' if args.dr5 else 'DR4')
        print("Returned query data: \n", returned_query)
        print(returned_query.info())

        # Save the queried data to a CSV file and a pickled .npy file
        output_csv_filename = "exoplanet_query_results.csv"
        returned_query.to_csv(output_csv_filename, index=False)
        print(f"Query results saved to {output_csv_filename}")
        output_npy_filename = "exoplanet_query_results.npy"
        np.save(output_npy_filename, returned_query)
        print(f"Query results saved to {output_npy_filename}")
        
        # Load the data back from the .npy file to verify saving worked and fit in
        #   with the work flow of loading a previous query result
        loaded_data = np.load("exoplanet_query_results.npy", allow_pickle=True)
        query_result_df = pd.DataFrame(loaded_data.tolist())
        print("Loaded query result from exoplanet_query_results.npy:")
        print(query_result_df)

    # Call the plotting functionality to make the sensitivity plots