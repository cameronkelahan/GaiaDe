import argparse
from html import parser
import numpy as np
import os
import pandas as pd
import plotting
import sys

# Local modules
import plotting
import query
import utilities

####################
# Defining constants
USAGE_ERROR_MESSAGE = '''\nUsage: python main.py <planet_id> OR <planet_ID_list_filename> plus optional flags (see below)
Example: python main.py Gaia DR3 123456789 OR python main.py planet_ids.txt --dr5
Accepted file formats are .txt and .csv
IDs are the whole ID and should include the acronym of the catalog. I.e. Gaia DR3 123456789 or TIC 123456
Accepted catalougue acronyms are "Gaia DR3", "HD", "HIP", and "TIC"
Optional flags:
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
        
        # print("BEFORE ADDING CAT ID TYPE: \n", planet_ids_df)
        # planet_ids_df["cat_id_type"] = "Unknown"
        # print("AFTER SETTING CAT ID TYPE COLUMN TO UNKNOWN: \n", planet_ids_df)
        # planet_ids_df.loc[planet_ids_df["ID"].str.startswith("Gaia DR3"), "cat_id_type"] = "gaia_dr3_id"
        # planet_ids_df.loc[planet_ids_df["ID"].str.startswith("TIC"), "cat_id_type"] = "tic_id"
        # planet_ids_df.loc[planet_ids_df["ID"].str.startswith("HIP"), "cat_id_type"] = "hip_name"
        # planet_ids_df.loc[planet_ids_df["ID"].str.startswith("HD"), "cat_id_type"] = "hd_name"

        # print("AFTER ADDING CAT ID TYPE: \n", planet_ids_df)
            
        print(f"Read {len(planet_ids_df)} planet IDs from file {file_path}")
        # print(planet_ids)
    
    # If there is no file extension found, assume direct input of one planet ID
    else:
        cat_id_type = 'single'

        try:
            int(sys.argv[1])
            print("ERROR: Invalid input format. If providing a single planet ID, ensure the last argument is the number part of the ID")
            print("       and that the catalogue acronym is included.")
            print(USAGE_ERROR_MESSAGE)
            sys.exit(1)
        except ValueError:
            pass

        # Check if the last arg is an int
        try:
            int(sys.argv[-1])
        except ValueError:
            print("ERROR: Invalid input format. If providing a single planet ID, ensure the last argument is the number part of the ID")
            print("       and that the catalogue acronym is included.")
            print(USAGE_ERROR_MESSAGE)
            sys.exit(1)

        # Create a dartaframe that holds the single planet ID and its catalogue type
        id_string = ""

        for arg in sys.argv[1:]:
            id_string += arg + " "

        planet_ids_df = pd.DataFrame({"ID": [id_string.strip()]})
        print(planet_ids_df)

        # # Check what type of ID is being input based on the the user input
        # # If a full ID is given, look for the catalogue acronym in the input
        # try:
        #     if sys.argv[1] == "Gaia" and sys.argv[2] == "DR3":
        #         int(sys.argv[3])
        #         # add a row to the dataframe with the planet ID and cat_id_type
        #         planet_ids_df = pd.DataFrame({'ID': ['Gaia DR3 ' + sys.argv[3]], 'cat_id_type': ['gaia_dr3_id']})
        #         print("PLANET IDS DF FROM DIRECT INPUT: \n", planet_ids_df)
        #         # planet_ids = sys.argv[3]
        #         # cat_id_type = 'gaia_dr3_id'
        #     elif sys.argv[1] == "TIC":
        #         int(sys.argv[2])
        #         planet_ids_df = pd.DataFrame({'ID': ['TIC ' + sys.argv[2]], 'cat_id_type': ['tic_id']})
        #         print("PLANET IDS DF FROM DIRECT INPUT: \n", planet_ids_df)
        #         # planet_ids = sys.argv[2]
        #         # cat_id_type = 'tic_id'
        #     elif sys.argv[1] == "HIP":
        #         int(sys.argv[2])
        #         planet_ids_df = pd.DataFrame({'ID': ['HIP ' + sys.argv[2]], 'cat_id_type': ['hip_name']})
        #         print("PLANET IDS DF FROM DIRECT INPUT: \n", planet_ids_df)
        #         # planet_ids = sys.argv[2]
        #         # cat_id_type = 'hip_name'
        #     elif sys.argv[1] == "HD":
        #         int(sys.argv[2])
        #         planet_ids_df = pd.DataFrame({'ID': ['HD ' + sys.argv[2]], 'cat_id_type': ['hd_name']})
        #         print("PLANET IDS DF FROM DIRECT INPUT: \n", planet_ids_df)
        #         # planet_ids = sys.argv[2]
        #         # cat_id_type = 'hd_name'
            
        #     # If only a single integer is given, assume it's just the number part of an ID and the user will specify the catalogue with a flag
        #     elif isinstance(int(sys.argv[1]),int):
        #         if len(sys.argv) < 3:
        #             raise ValueError("Not enough arguments provided")
        #         int(sys.argv[1])
        #         planet_ids_df = pd.DataFrame({'ID': [sys.argv[1]], 'cat_id_type': None})
        #         print("PLANET IDS DF: ", planet_ids_df)
        #     else:
        #         raise ValueError("Invalid input format")
        # except ValueError:
        #     print("INPUT ERROR")
        #     print(USAGE_ERROR_MESSAGE)
        #     sys.exit(1)
    return planet_ids_df, cat_id_type

def validate_catalog_input():

    if len(sys.argv) < 2:
        raise ValueError("No catalogue provided.")

    valid_single_catalogs = {"HD", "TIC", "HIP"}

    # Case 1: Gaia (needs DR3 or DR2)
    if sys.argv[1].lower() == "gaia":
        if len(sys.argv) < 3:
            raise ValueError("Gaia must be followed by DR3.")
        
        if sys.argv[2].upper() not in {"DR3"}:
            raise ValueError("Gaia must be followed by DR3.")

        return

    # Case 2: HD, TIC, HIP
    elif sys.argv[1].upper() in valid_single_catalogs:
        return

    else:
        raise ValueError(
            "Invalid catalogue. Must be one of: Gaia DR3, HD, TIC, or HIP."
        )

# Main execution
if __name__ == "__main__":

    # Create an argument parser and define the expected and possible arguments
    parser = argparse.ArgumentParser()
    
    # The only mandatory argument is the planet ID or the file containing the planet IDs (but a flag should be used if no full ID is given)
    parser.add_argument('planet_ids', nargs='*')
    
    # Optional flag that specifies using DR5 observation timeline
    parser.add_argument('--dr5', '--DR5', '--Dr5', action='store_true')

    # Optional flag that loads a previous query result from a .npy file instead of querying again
    parser.add_argument('--load_file', '--LOAD_FILE', '--Load_File')

    # Collect the parsed arguments
    args = parser.parse_args()

    # Prints out the args for debugging purposes
    print("Arguments parsed:")
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

        # Check that one of the appropriate catalogue acronyms is in the sys.argv if the cat_id_type is single


        # If the user fed in a single planet ID, validate the associated catalogue acronym
        try:
            if cat_id_type == 'single':
                # Check that sys.argv[1] is an acceptable catalogue acronym for simbad to locate
                validate_catalog_input()

        except ValueError:
            print("Error determining ID type. Please ensure you provide a valid ID or use the appropriate flag.")
            print(USAGE_ERROR_MESSAGE)
            sys.exit(1)
        
        print("FINAL PLANET IDS DF TO BE USED IN QUERY: \n", planet_ids)

        returned_query = query.gaia_query(planet_ids, data_release='DR5' if args.dr5 else 'DR4')
        print("Returned query data: \n", returned_query)
        print(returned_query.info())

        # QUERY QUALITY CHECKS
        # If distance is missing, check if parallax is viable (S/N > 10) and us that to estimate distance
        returned_query["distance_estimated_flag"] = 0
        snr_parallax = returned_query['parallax'] / returned_query['parallax_error']

        mask = (
            returned_query["distance_gspphot"].isna() &
            returned_query["parallax"].notna() &
            returned_query["parallax_error"].notna() &
            (returned_query["parallax"] > 0) &
            (snr_parallax >= 10)
        )

        returned_query.loc[mask, "distance_gspphot"] = (
            1000.0 / returned_query.loc[mask, "parallax"]
        )
        returned_query.loc[mask, "distance_estimated_flag"] = 1
        print(f"Estimated distances for {mask.sum()} stars (parallax S/N >= 10).")

        # Find any rows with NaNs
        nan_rows = returned_query[returned_query.isna().any(axis=1)]
        missing_info = nan_rows.apply(lambda row: row.index[row.isna()].tolist(), axis=1)
        nan_rows = nan_rows.copy()
        nan_rows['missing_columns'] = missing_info
        # For now, just drop the rows that contain an NaN
        clean_df = returned_query.drop(nan_rows.index)

        print("ROWS WITH NaNs (DROPPED ROWS): \n", nan_rows)

        # Possible way to estimate distance if missing, before checking for NaN rows
        #    - may want to only do this for rows with a certain S/N for the parallax measurement (>10?)
        # returned_query.fillna({'distance_gspphot': 1000.0 / df['parallax']})

        # Save the queried data to a CSV file and a pickled .npy file
        output_csv_filename = "gaia_query_results.csv"
        clean_df.to_csv(output_csv_filename, index=False)
        print(f"Query results saved to {output_csv_filename}")
        output_npy_filename = "gaia_query_results.pkl"
        clean_df.to_pickle(output_npy_filename)
        print(f"Query results saved to {output_npy_filename}")
        
        # Load the data back from the .npy file to verify saving worked and fit in
        #   with the work flow of loading a previous query result
        query_result_df = pd.read_pickle("gaia_query_results.pkl")
        print("Loaded query result from gaia_query_results.pkl:")
        print(query_result_df)


#######################################################################################
#    Calculate the astrometric signature and SNR grids for the queried/loaded data    #
#######################################################################################

    # Call the utility function to create a grid of 100x100 numbers for planet mass and orbital period
    #   evenly spaced in log space
    period_days_1D_array, mass_mjup_1D_array = utilities.period_mass_grid()
    # Calculate P^2/3) for teh sem_maj_axis calculation
    period_conversion_for_sem_maj_calculation = (period_days_1D_array/365.25)**(2/3)

    # Thus begins the for loop iterationg through the queried stellar data
    for star in query_result_df.itertuples(index=False):
        
        semi_major_axis_1D_array = utilities.semi_maj_axis_conversion(period_conversion_for_sem_maj_calculation, star.mass_flame)

        # Calculate the astrometric signaure grids for the queried exoplanet data
        astrometric_signature_grid = utilities.astrometric_signature_grid(star.mass_flame,
                                                                          star.distance_gspphot,
                                                                          semi_major_axis_1D_array,
                                                                          mass_mjup_1D_array)
    
        # THINK OF A TEST TO MAKE SURE THIS CALCULATION IS WORKING AS EXPECTED

        # Calculate the SNR1 values for each of the astrometric signaure values based on the star's
        #   g-magnitude
        snr_grid_theoretical, snr_grid_actual = utilities.snr_grid(astrometric_signature_grid,
                                                                   star.phot_g_mean_mag) 

        # Call the plotting functionality to make the sensitivity plots
        # TO DO:
        known_planets = None # declared for method purposes
        #   - add known planets functionality
        #   - query exoplanet archive for known planet information for the star and add to the plot
        # known_planets = [(0.349, 3.02),(1.152, 9.27)] # (AU, M_jup) for TOI-4600 b and c )not detectable)
        # known_planets = [(0.03, 0.024),(13.183, 5.909)] # for HD 155918 super jupiter (not detectable) GDR3 ID 5801950515627094400
        # known_planets = [(3.233, 24.128), (2.325, 22.609)] # for 2 planets around HD 81817 MISSING SOL MASS IN GAIA DATABASE
        # known_planets = [(0.073, 0.0387), (1.37, 7.6802)] # for TOI-1736 b and c (c is detectable) GDR3 ID 541725187117160960
        
        plotting.plot_snr_1_grid(semi_major_axis_1D_array,
                                  mass_mjup_1D_array,
                                  snr_grid_theoretical,
                                  title_suffix="Theoretical Deviation Angle",
                                  star_name=star.source_id,
                                  g_magnitude=star.phot_g_mean_mag,
                                  distance_pc=star.distance_gspphot,
                                  stellar_mass_solar=star.mass_flame,
                                  known_planets=known_planets)
        plotting.plot_snr_1_grid(semi_major_axis_1D_array,
                                  mass_mjup_1D_array,
                                  snr_grid_actual,
                                  title_suffix="Actual Deviation Angle",
                                  star_name=star.source_id,
                                  g_magnitude=star.phot_g_mean_mag,
                                  distance_pc=star.distance_gspphot,
                                  stellar_mass_solar=star.mass_flame,
                                  known_planets=known_planets)
    

    # # make fake matrtices for testing
    # snr_matrix = np.random.rand(10,10) * 10  # Random SNR values between 0 and 10
    # planet_masses = np.logspace(-1, 2, 10)  # Planet masses from 0.1 to 100 Jupiter masses
    # orbital_periods = np.logspace(0, 3, 10)  # Orbital periods from 1 to 1000 days

    # plotting.plot_sensitivity(snr_matrix, planet_masses, orbital_periods, title="Test Sensitivity Plot")