import numpy as np

# This file hosts numerous utility functions used across different modules

# NEEDED:
# - Use astropy units for calculations
# - astrometric signature function
#   - known params from query are distance and stellar mass
#   - planet mass and orbital period / semi-major axis are unknowns

# Calculate the astrometric signature (in mas) for a grid of planet masses and semi-major-axes
def astrometric_signature_grid(
    stellar_mass_solar,
    distance_pc,
    semi_major_axis_au,
    planet_masses_jup
):
    """
    Returns a 2D array of astrometric signatures (mas)
    Shape: (n_masses, n_au)
    """

    # Constant factor
    C = 0.95479 / (stellar_mass_solar * distance_pc)

    # Broadcasting outer product
    alpha_mas = (
        C
        * planet_masses_jup[:, None]
        * semi_major_axis_au[None, :]
    )

    return alpha_mas

# Based on the magnitude of the host star, assign theoretical and actual deviation angles
#   based on pre-defined functions; estimated from fig A.1 Lindegren et al. 2021 Gaia EDR3
def assign_deviation_angles(magnitude):
    if magnitude <= 8.25:
        theoretical = 0.0032103219442715437 * (1.5802904035394523**magnitude)
    elif 8.25 < magnitude <= 12:
        theoretical = 0.09773642956267346 * (0.9517614440673656**magnitude)
    elif magnitude > 12:
        theoretical = 0.00020571612193689604 * (1.6186445827673461**magnitude)
    else:
        theoretical = np.nan
    
    if magnitude <= 6:
        actual = 48.828124999999986 * (0.4**magnitude)
    elif 6 < magnitude <= 13.5:
        actual = 0.2822924808032303 * (0.9441806901029314**magnitude)
    elif magnitude > 13.5:
        actual = 0.00021046513935797287 * (1.6096194031076707**magnitude)
    else:
        actual = np.nan

    assert 'theoretical' in locals(), "Theoretical deviation angle not assigned!"
    assert 'actual' in locals(), "Actual deviation angle not assigned!"
    return theoretical, actual

# TO DO: Make the resolution of the period/mass grid based on config file input
#        - Still planning to add a smoothing funciton though
#        - Currently based on a 100x100 grid, which is likely too high?
def period_mass_grid():
    # Create a grid of RxC numbers (based on config) for planet masses and orbital periods (days)
    #   evenly spaced in log space
    planet_period = np.logspace(np.log10(10), np.log10(2000), 100)  # 10 → 2000 days
    # planet_period = np.logspace(np.log10(10), np.log10(4000), 100)  # 10 → 4000 days
    planet_masses = np.logspace(np.log10(0.3), np.log10(200), 100)  # 0.01 → 200 M_jup
    # print(planet_masses)
    # P, M = np.meshgrid(planet_period, planet_masses)
    return planet_period, planet_masses

# Helper functions for the 2nd (top) axis of the plots)
def period_to_a(P_days, stellar_mass_solar):
    return (stellar_mass_solar * (P_days / 365.25)**2)**(1/3)
def a_to_period(a_au, stellar_mass_solar):
    return 365.25 * np.sqrt(a_au**3 / stellar_mass_solar)

def semi_maj_axis_conversion(converted_period_years, stellar_mass_solar):
    return (converted_period_years * (stellar_mass_solar)**(1/3))

def snr_grid(alpha_grid, gaia_mag):
    theoretical_dev_angle, actual_dev_angle = assign_deviation_angles(gaia_mag)
    snr_1_grid_theoretical  = alpha_grid / theoretical_dev_angle
    snr_1_grid_actual  = alpha_grid / actual_dev_angle
    return snr_1_grid_theoretical, snr_1_grid_actual

# # JUST SET A SPECIFIC LIST OF AU TICKS TO ALWAYS USE FOR DR4 and DR5
# # SOMETHING LIKE 0.01 to 3 for DR4?

# # Stellar Paramters (temporary for testing; will be read in from config file/query)
# star_name = "GJ 317"
# tic_id = "TIC 118608254"

# # Create a grid of 100x100 numbers for planet mass and orbital period evenly spaced in log space
# planet_period = np.logspace(np.log10(10), np.log10(2000), 100)  # 10 → 2000 days
# # planet_period = np.logspace(np.log10(10), np.log10(4000), 100)  # 10 → 4000 days
# planet_masses = np.logspace(np.log10(0.3), np.log10(200), 100)  # 0.01 → 200 M_jup
# print(planet_masses)
# P, M = np.meshgrid(planet_period, planet_masses)

# # stellar_mass_solar = 1.0
# # distance_pc = 10.0
# # g_magnitude = 12 # Example G-magnitude for testing

# # stellar_mass_solar = 0.45 # TOI 6692
# # distance_pc = 310
# # g_magnitude = 11.578  # Example G-magnitude TOI-6692

# stellar_mass_solar = .402 # GJ 317
# distance_pc = 15.197 # GJ 317
# g_magnitude = 10.75  # Example G-magnitude GJ 317
# known_planets = [(1.138, 1.688), (5.04, 1.43)] # (AU, M_Jup) for GJ 317 b and c

# planet_period_year = planet_period / 365.25
# a_values = (stellar_mass_solar * planet_period_year**2)**(1/3)

# # Calculate the astrometric signature grid based on the input values
# # Quickly converts Period from days to years for Keplers 3rd law equation
# # (P^2 * St_Mass) ^ (1/3)
# # This is an estimate of the astrometric signature in mas
# # With units of years and solar masses to solve for AU, the grav constant value of the original
# #   equation converted to solar masses becomes a relatively small constant (39.46 AU^3/(year^2*M_sun))
# A, M = np.meshgrid(a_values, planet_masses)
# alpha_mas_grid = 0.95479 * M * A / stellar_mass_solar / distance_pc


# print("Astrometric signature grid shape:", alpha_mas_grid.shape)
# print("Sample astrometric signature values (mas):")
# print(alpha_mas_grid[:5, :5])

# # Determine the deviation angle of the star based on its G-magnitude
# theoretical_dev_angle, actual_dev_angle = assign_deviation_angles(g_magnitude)
# print(f"Theoretical Deviation Angle (mas): {theoretical_dev_angle}")
# print(f"Actual Deviation Angle (mas): {actual_dev_angle}")

# # Calculate the ratio of astrometric signature to deviation angle (SNR1)
# SNR_1_grid_theoretical  = alpha_mas_grid / theoretical_dev_angle
# SNR_1_grid_actual  = alpha_mas_grid / actual_dev_angle

# # Plot the astrometric signature grid for testing
# import matplotlib.pyplot as plt
# import matplotlib.colors as colors
# import matplotlib.ticker as ticker
# from matplotlib.lines import Line2D

# # PLOT ASTOMETRIC SIGNATURE COLOR PLOT
# fig, ax = plt.subplots(figsize=(10, 6))

# vmin = alpha_mas_grid[alpha_mas_grid > 0].min()
# vmax = alpha_mas_grid.max()

# # Set these as the bottom x-axis ticks

# ax.set_xlabel("Semi-Major Axis (AU)", fontsize=12)
# ax.set_xscale("log")
# ax.set_yscale("log")
# ax.set_ylabel("Planet Mass (Jupiter Masses)", fontsize=12)

# secax = ax.secondary_xaxis('top', functions=(a_to_period, period_to_a))
# secax.set_xlabel('Orbital Period [days]', fontsize=12)

# levels = levels = np.logspace(
#     np.log10(vmin),
#     np.log10(vmax),
#     100
# )

# contourplt = ax.contourf(
#     a_values,
#     planet_masses,
#     alpha_mas_grid,
#     levels=levels,
#     cmap='viridis',
#     norm=colors.LogNorm(
#         vmin=vmin,
#         vmax=vmax
#     )
# )

# # if known_planets:
# #     planets_outside_bounds = []
# #     for (a_au, m_jup) in known_planets:
# #         if a_au < a_values.min() or a_au > a_values.max():
# #             planets_outside_bounds.append((a_au, m_jup))
# #             continue
# #         if m_jup < planet_masses.min() or m_jup > planet_masses.max():
# #             planets_outside_bounds.append((a_au, m_jup))
# #             continue
# #         plt.plot(
# #             a_au,
# #             m_jup,
# #             marker='o',
# #             color='white',
# #             markersize=8,
# #             markeredgecolor='black',
# #             label='Known Planet'
# #         )
# #     plt.legend(loc='upper right')
# #     if len(planets_outside_bounds) > 0:
# #         print("Known planets outside plot bounds (not shown):", planets_outside_bounds)

# cbar = fig.colorbar(contourplt, ax=ax)
# cbar.set_label('Astrometric Signature (mas)', fontsize=12)

# # Force ticks at powers of 10
# cbar.locator = ticker.LogLocator(base=10.0)
# cbar.formatter = ticker.LogFormatterMathtext(base=10.0)
# cbar.update_ticks()

# fig.suptitle(
#     rf'$\alpha$ Signature Grid: {star_name} {tic_id}| '
#     f'G_mag={g_magnitude} | Dist={distance_pc} pc | '
#     rf'$M_\star$={stellar_mass_solar} $M_\odot$',
#     fontsize=12,
#     x=0.5,
#     ha='center'
# )

# plt.savefig('test_plots/astrometric_signature_grid.png', dpi=600)
# # plt.show()

# # Plot the SNR_1 grid with the SNR 1 value as a color bar, the x axis as period, and y axis as mass
# def plot_snr_1_grid(grid, title_suffix, star_name, g_magnitude, distance_pc, stellar_mass_solar,
#                     known_planets=None):
#     fig, ax = plt.subplots(figsize=(10, 6))
#     vmin_snr = grid[grid > 0].min()
#     vmax_snr = grid.max()

#     # Set these as the bottom x-axis ticks
#     ax.set_xlabel("Semi-Major Axis [AU]", fontsize=12)
#     ax.set_xscale("log")
#     ax.set_yscale("log")
#     ax.set_ylabel(f"Planet Mass [$M_J$]", fontsize=12)

#     secax = ax.secondary_xaxis('top', functions=(a_to_period, period_to_a))
#     secax.set_xlabel('Orbital Period [days]')

#     levels_snr = np.logspace(
#         np.log10(vmin_snr),
#         np.log10(vmax_snr),
#         100
#     )

#     contourplt_snr = ax.contourf(
#         a_values,
#         planet_masses,
#         grid,
#         levels=levels_snr,
#         cmap='viridis',
#         norm=colors.LogNorm(
#             vmin=vmin_snr,
#             vmax=vmax_snr
#         )
#     )

#     cbar = fig.colorbar(contourplt_snr, ax=ax)
#     cbar.set_label(f'$SNR_1$ ({title_suffix}) (mas)', fontsize=12)

#     # Force ticks at powers of 10
#     cbar.locator = ticker.LogLocator(base=10.0)
#     cbar.formatter = ticker.LogFormatterMathtext(base=10.0)
#     cbar.update_ticks()

#     # add a straight line where SNR1 = 1
#     plt.contour(
#         a_values,
#         planet_masses,
#         grid,
#         levels=[1],
#         colors='red',
#         linewidths=2,
#         linestyles='dashed'
#     )

#     # Create a proxy line for the legend
#     snr1_proxy = Line2D(
#         [0], [0],
#         color='red',
#         linestyle='dashed',
#         linewidth=2,
#         label=r'SNR$_1$ = 1'
#     )

#     # Add legend for the SNR_1=1 line
#     fig.legend(
#         handles=[snr1_proxy],
#         loc='upper left',
#         bbox_to_anchor=(0.12, 0.88),  # adjust if needed
#         frameon=True,
#         fontsize=10
#     )
    
#     # if known_planets:
#     #     planets_outside_bounds = []
#     #     for (a_au, m_jup) in known_planets:
#     #         if a_au < a_values.min() or a_au > a_values.max():
#     #             planets_outside_bounds.append((a_au, m_jup))
#     #             continue
#     #         if m_jup < planet_masses.min() or m_jup > planet_masses.max():
#     #             planets_outside_bounds.append((a_au, m_jup))
#     #             continue
#     #         plt.plot(
#     #             a_au,
#     #             m_jup,
#     #             marker='o',
#     #             color='white',
#     #             markersize=8,
#     #             markeredgecolor='black',
#     #             label='Known Planet'
#     #         )
#     #     plt.legend(loc='upper right')
#     #     if len(planets_outside_bounds) > 0:
#     #         print("Known planets outside plot bounds (not shown):", planets_outside_bounds)

#     fig.suptitle(
#         f'{title_suffix} $SNR_1$ Grid: {star_name} | '
#         f'G_mag={g_magnitude} | Dist={distance_pc} pc | '
#         rf'$M_\star$={stellar_mass_solar} $M_\odot$',
#         fontsize=12,
#         x=0.5,
#         ha='center'
#     )

#     plt.savefig(f'test_plots/{star_name}/{title_suffix}_snr1_grid.pdf', dpi=600)
#     plt.savefig(f'test_plots/{star_name}/{title_suffix}_snr1_grid.png', dpi=600)
#     # plt.show()

# # known_planets = [(1.138, 1.688), (5.04, 1.43)] # (AU, M_Jup) for GJ 317 b and c
# # known_planets = [(0.349, 3.02),(1.152, 9.27)] # (AU, M_jup) for TOI-4600 b and c

# # plot_snr_1_grid(SNR_1_grid_actual, 'DR3 Observed', known_planets)
# # plot_snr_1_grid(SNR_1_grid_theoretical, 'Theoretical', known_planets)

# ## TO DO:
# # - Remove dashed line showig SNR of 1
# # - Match Lammers et al. paper's AU limit (0.1 AU lower limit)
# # - Double check the calculations
# #  - Plot the planets from Wu 2026 Cold Jupiters paper
# #  - add symbols for where the planets sit in the plot space
# # - Incorporate a smoothing function and reduce resolution of the base arrays
# # - change color bar (match Lammers?); brighter colors means detectable, dark means not
# # OVERALL
# # - Make 3 types of plots
# #  1) Astrometric signature color plot
# #  2) SNR1 color plot
# #  3) SNR1 contour plot with number of observations considered (GOST)
# # Remove all hard-coded values
# # Implement Gaia database query
# # Add flag for --st_mass for a user to specify (would overwrite any queryed value)
