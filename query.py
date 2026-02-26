# This file queries the exoplanet archive, gaia archive, TIC catalog, etc. to locate
#   the desired planet based on user input and retrieve relevant data.

import numpy as np
import pandas as pd
import pyvo as vo
import re
import requests
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad

# Initialize TAP service for NASA Exoplanet Archive
service = vo.dal.TAPService("https://exoplanetarchive.ipac.caltech.edu/TAP")

# Converts python list into SQL readable (essentially drops the [] square brackets)
def sql_string_list(values):
    return ",".join(f"'{v}'" for v in values)

def exoplanet_query(planet_ids, data_release):
    if data_release == 'DR5':
        # This sets a limit of 9.5 years on orbital periods for DR5 observations
        # Unit in days
        orb_period = 3469.875
    else:
        # This is the limit for DR4 observations of 4.0 years
        # Unit in days
        orb_period = 1461  # Example value for DR4

    print(orb_period, type(orb_period))

    # Query Simbad to get Gaia DR3 IDs for the provided planet IDs (if they are not already Gaia DR3 IDs)
    #   This is necessary as we are going to query the Gaia archive, which relies on Gaia IDs


    # Group the planet IDs into lists
    gaia_ids = planet_ids.loc[planet_ids['cat_id_type'] == 'gaia_dr3_id', 'ID'].tolist()
    tic_ids = planet_ids.loc[planet_ids['cat_id_type'] == 'tic_id', 'ID'].tolist()
    hip_names = planet_ids.loc[planet_ids['cat_id_type'] == 'hip_name', 'ID'].tolist()
    hd_names = planet_ids.loc[planet_ids['cat_id_type'] == 'hd_name', 'ID'].tolist()

    # Build SQL WHERE clauses
    clauses = []

    if gaia_ids:
        gaia_ids_sql = sql_string_list(gaia_ids)
        clauses.append(f"gaia_dr3_id IN ({gaia_ids_sql})")
        print("Gaia IDs for query:", gaia_ids)
    if tic_ids:
        tic_ids_sql = sql_string_list(tic_ids)
        clauses.append(f"tic_id IN ({tic_ids_sql})")
    if hip_names:
        hip_names_sql = sql_string_list(hip_names)
        clauses.append(f"hip_name IN ({hip_names_sql})")
    if hd_names:
        hd_names_sql = sql_string_list(hd_names)
        clauses.append(f"hd_name IN ({hd_names_sql})")
    if not clauses:
        raise ValueError("No valid IDs to query")

    id_where = " OR ".join(clauses)

    """Query the NASA Exoplanet Archive for exoplanet data based on planet ID and type."""
    
    query = f'''SELECT pl_name, hostname, pl_letter, gaia_dr3_id, sy_snum,
                               sy_pnum, discoverymethod, pl_orbper, pl_orbperlim, pl_orbsmax,
                               pl_radj, pl_bmassj, pl_bmassprov, pl_orbeccen, st_teff, st_rad,
                               st_mass, st_met, st_metratio, rastr, ra, decstr, dec, sy_dist,
                               sy_plx, sy_gaiamag FROM ps
                               WHERE default_flag=1
                                    AND pl_orbper <= {orb_period}
                                    AND ({id_where})
                               ORDER BY pl_name'''
    print("Executing query:\n", query)
    
    resultset = service.search(f'''SELECT pl_name, hostname, pl_letter, gaia_dr3_id, sy_snum,
                               sy_pnum, discoverymethod, pl_orbper, pl_orbperlim, pl_orbsmax,
                               pl_radj, pl_bmassj, pl_bmassprov, pl_orbeccen, st_teff, st_rad,
                               st_raderr1, st_mass, st_met, st_metratio, rastr, ra, decstr, dec,
                               sy_dist, sy_plx, sy_gaiamag FROM ps
                               WHERE default_flag=1
                                    AND pl_orbper <= {orb_period}
                                    AND ({id_where})
                               ORDER BY pl_name''')

    result_df = resultset.to_table().to_pandas()

    # Check for missing planet ids / rows? where the query failed?

    return result_df

def querySimbad(IDs):
    """
    Batch query SIMBAD and return mapping of
    {input_id: matched_catalog_id}
    """

    customSimbad = Simbad()
    customSimbad.add_votable_fields("ids")

    result = customSimbad.query_objects(IDs)

    if result is None:
        return []

    print("Columns returned:", result.colnames)  # DEBUG LINE

    dr3_ids = []

    if "ids" not in result.colnames:
        raise RuntimeError(f"'ids' column missing. Columns: {result.colnames}")

    for row in result:
        ids_field = row["ids"]

        if isinstance(ids_field, bytes):
            ids_field = ids_field.decode()

        match = re.search(r"Gaia DR3 (\d+)", ids_field)

        if match:
            dr3_ids.append(match.group(1))

    return dr3_ids

def gaia_query(planet_ids, data_release):
    if data_release == 'DR5':
        # This sets a limit of 9.5 years on orbital periods for DR5 observations
        # Unit in days
        orb_period = 3469.875
    else:
        # This is the limit for DR4 observations of 4.0 years
        # Unit in days
        orb_period = 1461  # Example value for DR4

    # Group the ID column into a list of IDs for the Simbad query
    id_list = planet_ids['ID'].tolist()

    # Query Simbad to get Gaia DR3 IDs for the provided planet IDs (if they are not already Gaia DR3 IDs)
    #   This is necessary as we are going to query the Gaia archive, which relies on Gaia IDs

    gaiaDR3IDs = querySimbad(id_list)

    if len(gaiaDR3IDs) == 0:
        print("\nERROR:  Simbad returned an empty query.")
        print("Double check the given IDs.")
        raise ValueError
    if len(gaiaDR3IDs) < len(id_list):
        print("\nERROR:  Simbad returned fewer DR3 IDs than the given number of inputs.")
        print("Double check the given IDs.")
        raise ValueError
    else:
        print("Results: ", gaiaDR3IDs)

    sql_form_gaia_dr3_ids = sql_string_list(gaiaDR3IDs)

    # print("SQL formatted Gaia DR3 IDs for query: ", sql_form_gaia_dr3_ids)

    print("ABOUT TO QUERY")
    try:
        query = f'''SELECT gs.source_id, gs.ra, gs.ra_error, gs.dec, gs.dec_error,
                            gs.parallax, gs.parallax_error, gs.pm, gs.pmra, gs.pmra_error,
                            gs.pmdec, gs.pmdec_error, gs.distance_gspphot, gs.distance_gspphot_lower,
                            gs.distance_gspphot_upper, gs.astrometric_n_obs_al,
                            gs.astrometric_n_obs_ac, gs.astrometric_n_good_obs_al,
                            gs.astrometric_n_bad_obs_al, gs.matched_transits, gs.phot_g_mean_mag,
                            gs.phot_bp_mean_mag, gs.phot_rp_mean_mag, gs.teff_gspphot,
                            gs.teff_gspphot_lower, gs.teff_gspphot_upper, gs.logg_gspphot,
                            gs.logg_gspphot_lower, gs.logg_gspphot_upper, gs.mh_gspphot,
                            gs.mh_gspphot_lower, gs.mh_gspphot_upper, gs.astrometric_matched_transits,
                            gs.ag_gspphot, gs.ag_gspphot_lower, gs.ag_gspphot_upper,
                            ap.mass_flame, ap.mass_flame_lower, ap.mass_flame_upper, ap.radius_flame,
                            ap.radius_flame_lower, ap.radius_flame_upper
                    FROM gaiadr3.gaia_source AS gs
                    LEFT JOIN gaiadr3.astrophysical_parameters AS ap
                        ON gs.source_id = ap.source_id
                    WHERE gs.source_id IN ({sql_form_gaia_dr3_ids})'''
        # raise requests.exceptions.HTTPError("Simulated HTTP error for testing backup query")
        job = Gaia.launch_job_async(query)
        results = job.get_results()
        print(type(results))
    except requests.exceptions.HTTPError:
        print("\nERROR:  Gaia query failed with HTTPError.")
        print("This may be due to a temporary issue with the Gaia archive or an invalid query.")
        print("Please check the Gaia archive status and review the query for any potential issues.")

        print("\nIn the mean time, attempting backup query to Gaia@AIP service...")
        # Try backup database query if Gaia database is down
        # For Gaia@AIP service; a backup if the gaia database is down
        url = "https://gaia.aip.de/tap"
        # token = 'Token <your-token>'
        # Setup authorization
        tap_session = requests.Session()
        # tap_session.headers['Authorization'] = token
        tap_service = vo.dal.TAPService(url, session=tap_session)
        lang = "PostgreSQL"
        TAP_results = tap_service.run_sync(query, language=lang)
        results = TAP_results.to_table()
        print('...DONE\n')
        print(type(results))
        print(results)

    # If results are null or failed, use backup Gaia database; print message
    # TO DO

    results_df = results.to_pandas()

    # Check for missing planet ids / rows? where the query failed?

    return results_df