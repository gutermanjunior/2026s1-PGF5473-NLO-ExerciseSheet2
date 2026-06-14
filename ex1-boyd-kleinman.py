#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# PROJECT
# =============================================================================
# Name:
#     Boyd-Kleinman Optimization for Second Harmonic Generation (SHG)
#
# Description:
#     Numerical evaluation and optimization of the Boyd-Kleinman overlap
#     integral h(σ, ξ) used in nonlinear optics for Second Harmonic Generation.
#
# Features:
#     • Numerical computation of h(σ, ξ)
#     • Global optimum estimation via constrained optimization
#     • 2D contour map visualization
#     • Automatic optimum point identification
#     • Export to PDF
#     • Export to SVG
#     • High-resolution PNG export
#
# Mathematical Model:
#     Boyd-Kleinman focusing theory for Gaussian beam frequency conversion.
#
# Dependencies:
#     numpy
#     scipy
#     matplotlib
#
# Author:
#     <Your Name>
#
# Version:
#     2.0
#
# Date:
#     2026
#
# =============================================================================
# SOFTWARE ENGINEERING NOTES
# =============================================================================
#
# Export System:
#     Export formats can be enabled or disabled individually through the
#     configuration section below.
#
# Supported Formats:
#     - PDF  (vector)
#     - SVG  (vector)
#     - PNG  (high resolution raster)
#
# PNG Resolution:
#     Width is controlled through PNG_TARGET_WIDTH_PX.
#     Height is automatically determined from figure proportions.
#
# Recommended Values:
#     4000 px  -> Publication quality
#     6000 px  -> High-end journal quality
#     8000 px  -> Large-format printing
#
# =============================================================================


# =============================================================================
# IMPORTS
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt

from scipy.integrate import quad
from scipy.optimize import minimize


# =============================================================================
# USER CONFIGURATION
# =============================================================================
#
# Enable or disable each export format independently.
#

EXPORT_PDF = False
EXPORT_SVG = False
EXPORT_PNG = False


# Output filenames (without automatic generation)
PDF_FILENAME = "boyd_kleinman_plot.pdf"
SVG_FILENAME = "boyd_kleinman_plot.svg"
PNG_FILENAME = "boyd_kleinman_plot.png"


# PNG target width in pixels
#
# Example:
#   3000
#   4000
#   6000
#   8000
#
PNG_TARGET_WIDTH_PX = 6000


# =============================================================================
# MATHEMATICAL CORE
# =============================================================================

def boyd_kleinman_integral(sigma, xi):
    """
    Compute the dimensionless Boyd-Kleinman efficiency factor h(σ, ξ).

    Parameters
    ----------
    sigma : float
        Normalized phase mismatch parameter.

    xi : float
        Focusing parameter.

    Returns
    -------
    float
        Efficiency factor h(σ, ξ).
    """

    if xi <= 0:
        return 0.0

    # Symmetric reduction integrand
    integrand = (
        lambda tau:
        (np.cos(sigma * tau) +
         tau * np.sin(sigma * tau))
        /
        (1.0 + tau**2)
    )

    integral, _ = quad(
        integrand,
        0,
        xi
    )

    return (2.0 / xi) * (integral ** 2)


# Vectorized version for mesh/grid evaluations
v_bk_integral = np.vectorize(boyd_kleinman_integral)


# =============================================================================
# OPTIMIZATION UTILITIES
# =============================================================================

def objective_function(x):
    """
    Objective function for numerical optimization.

    Since scipy.optimize.minimize performs minimization,
    we return -h in order to locate the maximum.
    """

    sigma, xi = x

    if xi <= 0.01:
        return 0.0

    return -boyd_kleinman_integral(sigma, xi)


# =============================================================================
# EXPORT UTILITIES
# =============================================================================

def calculate_png_dpi(
        target_width_px,
        figure_width_inches):
    """
    Compute the DPI necessary to achieve a desired image width.

    Parameters
    ----------
    target_width_px : int
        Desired PNG width in pixels.

    figure_width_inches : float
        Figure width in inches.

    Returns
    -------
    float
        DPI value.
    """

    return target_width_px / figure_width_inches


def export_figure(fig):
    """
    Export figure according to user configuration.
    """

    figure_width_inches = fig.get_size_inches()[0]

    png_dpi = calculate_png_dpi(
        PNG_TARGET_WIDTH_PX,
        figure_width_inches
    )

    print("\n=== Export Configuration ===")

    if EXPORT_PDF:
        fig.savefig(
            PDF_FILENAME,
            backend="pdf",
            bbox_inches="tight"
        )

        print(f"PDF exported: {PDF_FILENAME}")

    if EXPORT_SVG:
        fig.savefig(
            SVG_FILENAME,
            format="svg",
            bbox_inches="tight"
        )

        print(f"SVG exported: {SVG_FILENAME}")

    if EXPORT_PNG:
        fig.savefig(
            PNG_FILENAME,
            format="png",
            dpi=png_dpi,
            bbox_inches="tight"
        )

        print(
            f"PNG exported: {PNG_FILENAME} "
            f"(≈ {PNG_TARGET_WIDTH_PX} px width)"
        )


# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():

    # =========================================================================
    # STEP 1
    # Numerical optimization
    # =========================================================================

    print("Searching for Boyd-Kleinman optimum...")

    initial_guess = [0.5, 2.5]

    bounds = [
        (0.0, 2.0),
        (0.1, 10.0)
    ]

    result = minimize(
        objective_function,
        initial_guess,
        bounds=bounds,
        method="L-BFGS-B"
    )

    sigma_opt, xi_opt = result.x
    h_max = -result.fun

    # =========================================================================
    # STEP 2
    # Report optimization results
    # =========================================================================

    print("\n=== Boyd-Kleinman Optimization Results ===")

    print(
        f"Optimum focusing parameter (xi): "
        f"{xi_opt:.6f}"
    )

    print(
        f"Optimum phase mismatch (sigma): "
        f"{sigma_opt:.6f}"
    )

    print(
        f"Maximum efficiency factor h(max): "
        f"{h_max:.6f}"
    )

    # =========================================================================
    # STEP 3
    # Generate visualization grid
    # =========================================================================

    sigma_vec = np.linspace(
        -1.0,
        2.5,
        150
    )

    xi_vec = np.linspace(
        0.1,
        10.0,
        150
    )

    Sigma, Xi = np.meshgrid(
        sigma_vec,
        xi_vec
    )

    print("\nEvaluating grid for visualization...")

    H = v_bk_integral(
        Sigma,
        Xi
    )

    # =========================================================================
    # STEP 4
    # Figure creation
    # =========================================================================

    FIG_WIDTH = 7.0
    FIG_HEIGHT = 5.5

    fig = plt.figure(
        figsize=(FIG_WIDTH, FIG_HEIGHT),
        dpi=130
    )

    # =========================================================================
    # STEP 5
    # Contour visualization
    # =========================================================================

    contour = plt.contourf(
        Sigma,
        Xi,
        H,
        levels=30,
        cmap="viridis"
    )

    # =========================================================================
    # STEP 6
    # Colorbar
    # =========================================================================

    cbar = plt.colorbar(contour)

    cbar.set_label(
        r"Efficiency Factor $h(\sigma,\xi)$",
        fontsize=11
    )

    # =========================================================================
    # STEP 7
    # Highlight optimum point
    # =========================================================================

    plt.plot(
        sigma_opt,
        xi_opt,
        marker="*",
        color="red",
        markersize=10,
        linestyle="none",
        label=(
            f"Maximum: "
            f"$\\xi={xi_opt:.2f}$, "
            f"$\\sigma={sigma_opt:.2f}$"
        )
    )

    # =========================================================================
    # STEP 8
    # Axis formatting
    # =========================================================================

    plt.title(
        "Boyd-Kleinman Optimization Landscape",
        fontsize=12,
        fontweight="bold",
        pad=12
    )

    plt.xlabel(
        r"Normalized Phase Mismatch "
        r"$\sigma=\frac{1}{2}b\Delta k$",
        fontsize=11
    )

    plt.ylabel(
        r"Focusing Parameter "
        r"$\xi=L/b$",
        fontsize=11
    )

    plt.xlim(
        -1.0,
        2.5
    )

    plt.ylim(
        0.1,
        10.0
    )

    plt.grid(
        True,
        linestyle=":",
        alpha=0.5
    )

    plt.legend(
        loc="upper right",
        framealpha=0.9
    )

    plt.tight_layout()

    # =========================================================================
    # STEP 9
    # Export selected formats
    # =========================================================================

    export_figure(fig)

    # =========================================================================
    # STEP 10
    # Display
    # =========================================================================

    plt.show()


# =============================================================================
# PROGRAM ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()