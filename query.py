# This file queries the exoplanet archive, gaia archive, TIC catalog, etc. to locate
#   the desired planet based on user input and retrieve relevant data.

import numpy as np
import pandas as pd
import pyvo as vo

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
                               st_raderr1, st_mass, st_met, st_metratio, rastr, ra, decstr, dec,
                               sy_dist, sy_plx, sy_gaiamag FROM ps
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