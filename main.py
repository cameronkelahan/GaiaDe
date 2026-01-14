# define the coomand line inputs and parse them
import argparse
from html import parser
import os
import pandas as pd
import requests
import sys

import query

def interpret_user_input():
    # Variable that tracks the catalogue ID type
    cat_id_type = None
    
    if sys.argv[1].endswith('.txt') or sys.argv[1].endswith('.csv'):
        # Records if the file is a .txt or a .csv (used for parsing purposes later)
        file_extension = os.path.splitext(sys.argv[1])[1]
        print(f"File extension detected: {file_extension}")
        file_path = sys.argv[1]
        
        # Sets the catalogue ID type to the file extension initially (for later use)
        cat_id_type = file_extension
        
        # If there is no file, throw an error and exit
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            print("Usage: python main.py <planet_id> OR <planet_ID_list_filename> plus optional flags (see below)")
            print("Example: python main.py Gaia DR3 12345678 OR python main.py planet_ids.txt --dr5")
            print("Accepted file formats are .txt and .csv")
            print("IDs are the whole ID and should include the acronym of the catalog. I.e. Gaia DR3 123456789 or TIC 123456")
            print("Optional flags:")
            # specify gaia too
            print("  --tic      : Lookup based on TIC catalog ID")
            print("  --hipp     : Lookup based on Hipparcos catalog ID")
            print("  --hd       : Lookup based on Henry Draper catalog ID")
            print("  --dr5      : Calculate based on DR5 observaton timeline (DR4 is default)")
            sys.exit(1)
        
        # If it is a csv or txt file, parse the file appropriately to get the planet IDs
        if file_extension == '.csv':
            df = pd.read_csv(file_path, header=None)
            planet_ids = df.iloc[0].tolist()
        else:
            with open(file_path, 'r') as f:
                planet_ids = [line.strip(",\n") for line in f if line.strip()]
        print(f"Read {len(planet_ids)} planet IDs from file {file_path}")
        print(planet_ids)
    
    # If there is no file extension found, assume direct input of one planet ID
    else:
        
        # Check what type of ID is being input based on the the user input
        # If a full ID is given, look for the catalogue acronym in the input
        try:
            if sys.argv[1] == "Gaia" and sys.argv[2] == "DR3":
                int(sys.argv[3])
                planet_ids = sys.argv[3]
                cat_id_type = 'gaia_dr3_id'
            elif sys.argv[1] == "TIC":
                int(sys.argv[2])
                planet_ids = sys.argv[2]
                cat_id_type = 'tic_id'
            elif sys.argv[1] == "HIP":
                int(sys.argv[2])
                planet_ids = sys.argv[2]
                cat_id_type = 'hip_name'
            elif sys.argv[1] == "HD":
                int(sys.argv[2])
                planet_ids = sys.argv[2]
                cat_id_type = 'hd_name'
            
            # If only a single integer is given, assume it's just the number part of an ID and the user will specify the catalogue with a flag
            elif isinstance(int(sys.argv[1]),int):
                if len(sys.argv) < 3:
                    raise ValueError("Not enough arguments provided")
                int(sys.argv[1])
                planet_ids = sys.argv[1]
                print("PLANET IDS: ", planet_ids)
            else:
                raise ValueError("Invalid input format")
        except ValueError:
            print("Input error")
            print("Usage: python main.py <planet_id> OR <planet_ID_list_filename>, optional flags (see below)")
            print("Example: python main.py Gaia DR3 12345678 OR python main.py planet_ids.txt --dr5")
            print("IDs are the whole ID and should include the acronym of the catalog. I.e. Gaia DR3 123456789 or TIC 123456")
            print("If you have the whole ID, you do not have to add a flag to specify the catalogue.")
            print("If you only have the number values of the IDs, add the appropriate flag to the end to specify the catalogue.")
            print("e.g. python main.py 123456789 --hd or python main.py planet_ids.csv --tic")
            print("Optional flags:")
            print("  --gaiadr3  : Lookup based on Gaia DR3 catalog IDs")
            print("  --tic      : Lookup based on TIC catalog IDs")
            print("  --hipp     : Lookup based on Hipparcos catalog IDs")
            print("  --hd       : Lookup based on Henry Draper catalog IDs")
            print("  --dr5      : Calculate based on DR5 observaton timeline (DR4 is default)")
            sys.exit(1)
    return planet_ids, cat_id_type

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

    ## 1) Interpret the command line arguments to obtain planet IDs and the catalogue ID type
    planet_ids, cat_id_type = interpret_user_input()

    # Check if the multi_cat flag is set for the input file type
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

        # Call to the parse_file module to parse the file and prep the planet IDs for the Query module

    try:
        if cat_id_type is None:
            if args.gaiadr3:
                cat_id_type = 'gaia_dr3_id'
            elif args.tic:
                cat_id_type = 'tic_id'
            elif args.hipp:
                cat_id_type = 'hip_name'
            elif args.hd:
                cat_id_type = 'hd_name'
            elif args.multi_cat:
                cat_id_type = 'multi_cat'
            else:
                raise ValueError("No catalogue type specified")
    except ValueError:
        print("Error determining ID type. Please ensure you provide a valid ID or use the appropriate flag.")
        sys.exit(1)

    print(f"Using ID type: {cat_id_type}")



    # planet_ids, args = main()

    # if args.tic:
    #     cat_id_type = 'tic'
    # elif args.hipp:
    #     cat_id_type = 'hipparcos'
    # elif args.hd:
    #     cat_id_type = 'henry_draper'
    # else:
    #     cat_id_type = 'gaia'

    # query.get_planet_data(planet_ids, cat_id_type=cat_id_type)