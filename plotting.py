import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
import numpy as np
import os
from matplotlib.lines import Line2D

import utilities

####################################################################################################
#    This file creates the astromtric and sensitivity plots based on the queried exoplanet data    #
####################################################################################################

# Plots the astrometric signature grid for the queried stars in the given mass/sem_maj_axis grid
def plot_astrometric_sig():
    pass

# Receives matrix of SNR values and makes sensitivity plot based on the values in that grid/matrix
def plot_snr_1_grid(semi_major_axis_1D_array, planet_masses_1D_array, grid, title_suffix,
                    star_name, g_magnitude, distance_pc, stellar_mass_solar, known_planets=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    vmin_snr = grid[grid > 0].min()
    vmax_snr = grid.max()

    # Set these as the bottom x-axis ticks
    ax.set_xlabel("Semi-Major Axis [AU]", fontsize=12)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylabel(f"Planet Mass [$M_J$]", fontsize=12)
    secax = ax.secondary_xaxis('top',
                               functions=(
                                   lambda a: utilities.a_to_period(a, stellar_mass_solar),
                                   lambda P: utilities.period_to_a(P, stellar_mass_solar)
                                         )
                              )
    secax.set_xlabel('Orbital Period [days]')

    levels_snr = np.logspace(
        np.log10(vmin_snr),
        np.log10(vmax_snr),
        100
    )

    contourplt_snr = ax.contourf(
        semi_major_axis_1D_array,
        planet_masses_1D_array,
        grid,
        levels=levels_snr,
        cmap='viridis',
        norm=colors.LogNorm(
            vmin=vmin_snr,
            vmax=vmax_snr
        )
    )

    cbar = fig.colorbar(contourplt_snr, ax=ax)
    cbar.set_label(f'$SNR_1$ ({title_suffix}) (mas)', fontsize=12)

    # Force ticks at powers of 10
    cbar.locator = ticker.LogLocator(base=10.0)
    cbar.formatter = ticker.LogFormatterMathtext(base=10.0)
    cbar.update_ticks()

    # add a straight line where SNR1 = 1
    plt.contour(
        semi_major_axis_1D_array,
        planet_masses_1D_array,
        grid,
        levels=[1],
        colors='red',
        linewidths=2,
        linestyles='dashed'
    )

    # Create a proxy line for the legend
    snr1_proxy = Line2D(
        [0], [0],
        color='red',
        linestyle='dashed',
        linewidth=2,
        label=r'SNR$_1$ = 1'
    )

    # Add legend for the SNR_1=1 line
    fig.legend(
        handles=[snr1_proxy],
        loc='upper left',
        bbox_to_anchor=(0.12, 0.88),  # adjust if needed
        frameon=True,
        fontsize=10
    )
    
    if known_planets:
        # print("ADDING A PLANET")
        planets_outside_bounds = []
        for (a_au, m_jup) in known_planets:
            if a_au < semi_major_axis_1D_array.min() or a_au > semi_major_axis_1D_array.max():
                planets_outside_bounds.append((a_au, m_jup))
                continue
            if m_jup < planet_masses_1D_array.min() or m_jup > planet_masses_1D_array.max():
                planets_outside_bounds.append((a_au, m_jup))
                continue
            plt.plot(
                a_au,
                m_jup,
                marker='o',
                color='white',
                markersize=8,
                markeredgecolor='black',
                label='Known Planet'
            )
        plt.legend(loc='upper right')
        if len(planets_outside_bounds) > 0:
            print("Known planets outside plot bounds (not shown):", planets_outside_bounds)

    fig.suptitle(
        f'{title_suffix} $SNR_1$ Grid: {star_name} | '
        f'G_mag={g_magnitude} | Dist={distance_pc} pc | '
        rf'$M_\star$={stellar_mass_solar} $M_\odot$',
        fontsize=12,
        x=0.5,
        ha='center'
    )

    # Check if the filepath exists, if not create it
    if not os.path.exists('plots'):
        os.makedirs('plots')
    if not os.path.exists(f'plots/{star_name}'):
        os.makedirs(f'plots/{star_name}')

    plt.savefig(f'plots/{star_name}/{title_suffix}_snr1_grid.pdf', dpi=600)
    plt.savefig(f'plots/{star_name}/{title_suffix}_snr1_grid.png', dpi=600)
    # plt.show()

    plt.close()