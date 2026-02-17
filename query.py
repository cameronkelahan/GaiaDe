# This file queries the exoplanet archive, gaia archive, TIC catalog, etc. to locate
#   the desired planet based on user input and retrieve relevant data.

import numpy as np
import pandas as pd
import pyvo as vo
import re
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

def querySimbad(fromIDs, toID="Gaia DR3"):
    """
    Batch query SIMBAD and return mapping of
    {input_id: matched_catalog_id}
    """

    customSimbad = Simbad()
    customSimbad._VOTABLE_FIELDS = []
    customSimbad.add_votable_fields("ids")

    result = customSimbad.query_objects(fromIDs)
    # print(result)

    if result is None:
        return []

    dr3_ids = []

    for row in result:
        print(row)
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

    # Grouo the ID column into a list of IDs for the Simbad query
    id_list = planet_ids['ID'].tolist()

    # Query Simbad to get Gaia DR3 IDs for the provided planet IDs (if they are not already Gaia DR3 IDs)
    #   This is necessary as we are going to query the Gaia archive, which relies on Gaia IDs
    gaiaDR3IDs = querySimbad(id_list)

    if gaiaDR3IDs is not None:
        print("RESULT: ", gaiaDR3IDs)
    else:
        print("not found")

    sql_form_gaia_dr3_ids = sql_string_list(gaiaDR3IDs)

    print("SQL formatted Gaia DR3 IDs for query: ", sql_form_gaia_dr3_ids)

    query = f'''SELECT gs.source_id, gs.source_id, gs.parallax, gs.parallax_error, gs.distance_gspphot,
                        aps.distance_gspphot_marcs, ap.distance_gspphot,
                        gs.astrometric_n_obs_al,
                        gs.astrometric_n_obs_ac, gs.astrometric_n_good_obs_al, gs.astrometric_n_bad_obs_al,
                        gs.phot_g_mean_mag, gs.teff_gspphot, gs.logg_gspphot, gs.mh_gspphot, gs.astrometric_matched_transits,
                        ap.mass_flame, ap.radius_flame
                FROM gaiadr3.gaia_source AS gs
                LEFT JOIN gaiadr3.astrophysical_parameters AS ap
                    ON gs.source_id = ap.source_id
                LEFT JOIN gaiadr3.astrophysical_parameters_supp AS aps
                    ON gs.source_id = aps.source_id
                WHERE gs.source_id IN ({sql_form_gaia_dr3_ids})'''
    job = Gaia.launch_job_async(query)
    results = job.get_results()

    # If results are null or failed, use backup Gaia database; print message

    results_df = results.to_pandas()

    # Check for missing planet ids / rows? where the query failed?

    return results_df