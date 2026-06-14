#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# PROJECT
# =============================================================================
# Name:
#     Interactive Boyd-Kleinman Simulator
#
# Description:
#     Interactive graphical simulator for exploring the influence of the
#     focusing parameter (ξ) and normalized phase mismatch (σ) on second
#     harmonic generation (SHG) efficiency according to Boyd-Kleinman theory.
#
# Features:
#     • Real-time slider control
#     • Dynamic efficiency calculation
#     • Boyd-Kleinman theoretical optimum reference
#     • Interactive visualization
#     • Export to PDF
#     • Export to SVG
#     • Export to high-resolution PNG
#     • Scientific publication-ready figures
#
# Mathematical Model:
#     Boyd-Kleinman focusing theory for nonlinear frequency conversion.
#
# Dependencies:
#     numpy
#     matplotlib
#     scipy
#
# Version:
#     2.0
#
# =============================================================================
# SOFTWARE ENGINEERING NOTES
# =============================================================================
#
# Export Formats:
#     PDF : Vector format suitable for publications.
#     SVG : Vector format suitable for editing.
#     PNG : High-resolution raster image.
#
# PNG Resolution:
#     Controlled through PNG_TARGET_WIDTH_PX.
#
# Typical Values:
#     3000 px -> Good quality
#     6000 px -> Publication quality
#     8000 px -> Large-format printing
#
# =============================================================================


# =============================================================================
# IMPORTS
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Slider
from matplotlib.widgets import Button

from scipy.integrate import quad


# =============================================================================
# EXPORT CONFIGURATION
# =============================================================================

EXPORT_PDF = True
EXPORT_SVG = True
EXPORT_PNG = True


# Output filenames
PDF_FILENAME = "boyd_kleinman_interactive.pdf"
SVG_FILENAME = "boyd_kleinman_interactive.svg"
PNG_FILENAME = "boyd_kleinman_interactive.png"


# Desired PNG width
PNG_TARGET_WIDTH_PX = 6000


# =============================================================================
# EXPORT UTILITIES
# =============================================================================

def calculate_png_dpi(
        target_width_px,
        figure_width_inches):
    """
    Calculate the DPI necessary to achieve a target width in pixels.

    Parameters
    ----------
    target_width_px : int
        Desired image width.

    figure_width_inches : float
        Width of the figure in inches.

    Returns
    -------
    float
        Required DPI value.
    """

    return target_width_px / figure_width_inches


def export_figure(fig):
    """
    Export figure according to user settings.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure object to export.
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

        print(f"PDF exported : {PDF_FILENAME}")

    if EXPORT_SVG:

        fig.savefig(
            SVG_FILENAME,
            format="svg",
            bbox_inches="tight"
        )

        print(f"SVG exported : {SVG_FILENAME}")

    if EXPORT_PNG:

        fig.savefig(
            PNG_FILENAME,
            format="png",
            dpi=png_dpi,
            bbox_inches="tight"
        )

        print(
            f"PNG exported : {PNG_FILENAME}"
            f" (~{PNG_TARGET_WIDTH_PX}px width)"
        )

    print("Export completed successfully.\n")


# =============================================================================
# SIMULATOR CLASS
# =============================================================================

class SimuladorBoydKleinman:

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def __init__(self):

        # ---------------------------------------------------------------------
        # Boyd-Kleinman theoretical optimum values
        # ---------------------------------------------------------------------

        self.xi_opt = 2.84
        self.sigma_opt = 0.57

        # ---------------------------------------------------------------------
        # Sigma sampling grid used to draw the efficiency curve
        # ---------------------------------------------------------------------

        self.sigma_range = np.linspace(
            -1.0,
            3.0,
            200
        )

        # ---------------------------------------------------------------------
        # Figure and axis creation
        # ---------------------------------------------------------------------

        self.fig, self.ax = plt.subplots(
            figsize=(10, 7)
        )

        plt.subplots_adjust(
            left=0.10,
            bottom=0.35,
            right=0.90,
            top=0.90
        )

        # ---------------------------------------------------------------------
        # Initial data calculation
        # ---------------------------------------------------------------------

        h_iniciais = self.calcular_curva_h(
            self.sigma_range,
            self.xi_opt
        )

        h_ponto = self.h_integral(
            self.sigma_opt,
            self.xi_opt
        )

        # ---------------------------------------------------------------------
        # Main curve
        # ---------------------------------------------------------------------

        self.linha, = self.ax.plot(
            self.sigma_range,
            h_iniciais,
            lw=2.5,
            color='#2c3e50',
            label=r'Curva $h(\sigma)$ para o $\xi$ atual'
        )

        # ---------------------------------------------------------------------
        # Current operating point
        # ---------------------------------------------------------------------

        self.ponto, = self.ax.plot(
            [self.sigma_opt],
            [h_ponto],
            'ro',
            markersize=9,
            label='Posição Atual'
        )

        # ---------------------------------------------------------------------
        # Theoretical optimum reference line
        # ---------------------------------------------------------------------

        self.linha_max_teorico = self.ax.axvline(
            x=self.sigma_opt,
            color='r',
            linestyle='--',
            alpha=0.4,
            label='Ótimo Teórico ($\\sigma=0.57$)'
        )

        # ---------------------------------------------------------------------
        # Main graph formatting
        # ---------------------------------------------------------------------

        self.ax.set_xlim(
            -1.0,
            3.0
        )

        self.ax.set_ylim(
            -0.1,
            2.4
        )

        self.ax.set_xlabel(
            r'Descasamento de Fase Normalizado '
            r'$\sigma = \frac{1}{2}b\Delta k$',
            fontsize=11
        )

        self.ax.set_ylabel(
            r'Fator de Eficiência $h(\sigma,\xi)$',
            fontsize=11
        )

        self.ax.set_title(
            'Simulador Boyd-Kleinman: '
            'Otimização da Geração de Segundo Harmônico',
            fontweight='bold',
            pad=15
        )

        self.ax.grid(
            True,
            linestyle=':',
            alpha=0.7
        )

        self.ax.legend(
            loc='upper left'
        )

        # ---------------------------------------------------------------------
        # Information panel
        # ---------------------------------------------------------------------

        props_caixa = dict(
            boxstyle='round',
            facecolor='wheat',
            alpha=0.4
        )

        self.texto_info = self.ax.text(
            0.65,
            0.95,
            '',
            transform=self.ax.transAxes,
            verticalalignment='top',
            fontsize=10,
            bbox=props_caixa
        )

        # ---------------------------------------------------------------------
        # Widget axes
        # ---------------------------------------------------------------------

        cor_eixo = 'lightgoldenrodyellow'

        ax_xi = plt.axes(
            [0.15, 0.20, 0.65, 0.03],
            facecolor=cor_eixo
        )

        ax_sigma = plt.axes(
            [0.15, 0.13, 0.65, 0.03],
            facecolor=cor_eixo
        )

        ax_export = plt.axes(
            [0.60, 0.04, 0.15, 0.05]
        )

        ax_reset = plt.axes(
            [0.78, 0.04, 0.15, 0.05]
        )

        # ---------------------------------------------------------------------
        # Slider initialization
        # ---------------------------------------------------------------------

        self.slider_xi = Slider(
            ax_xi,
            r'Focalização $\xi$',
            0.1,
            10.0,
            valinit=self.xi_opt,
            valstep=0.01
        )

        self.slider_sigma = Slider(
            ax_sigma,
            r'Phase Mismatch $\sigma$',
            -1.0,
            3.0,
            valinit=self.sigma_opt,
            valstep=0.01
        )

                # ---------------------------------------------------------------------
        # Button initialization
        # ---------------------------------------------------------------------

        self.btn_export = Button(
            ax_export,
            'Export',
            color='whitesmoke',
            hovercolor='0.9'
        )

        self.btn_reset = Button(
            ax_reset,
            'Reset (Ótimo)',
            color='whitesmoke',
            hovercolor='0.9'
        )

        # ---------------------------------------------------------------------
        # Event connections
        # ---------------------------------------------------------------------

        self.slider_xi.on_changed(
            self.atualizar
        )

        self.slider_sigma.on_changed(
            self.atualizar
        )

        self.btn_reset.on_clicked(
            self.resetar
        )

        self.btn_export.on_clicked(
            self.exportar
        )

        # ---------------------------------------------------------------------
        # Initial draw
        # ---------------------------------------------------------------------

        self.atualizar(None)

    # =========================================================================
    # NUMERICAL MODEL
    # =========================================================================

    def h_integral(
            self,
            sigma,
            xi):
        """
        Evaluate the Boyd-Kleinman overlap integral.

        Parameters
        ----------
        sigma : float
            Normalized phase mismatch.

        xi : float
            Focusing parameter.

        Returns
        -------
        float
            Efficiency factor h(sigma, xi).
        """

        if xi <= 0:
            return 0.0

        # ---------------------------------------------------------------------
        # Symmetric reduction integrand
        # ---------------------------------------------------------------------

        def integrando(tau):

            return (
                np.cos(sigma * tau)
                +
                tau * np.sin(sigma * tau)
            ) / (
                1.0 + tau**2
            )

        valor_integral, _ = quad(
            integrando,
            0,
            xi
        )

        return (
            2.0 / xi
        ) * (
            valor_integral ** 2
        )

    def calcular_curva_h(
            self,
            vetor_sigma,
            xi):
        """
        Compute h(sigma) over a vector of sigma values.

        Parameters
        ----------
        vetor_sigma : ndarray
            Sigma sampling points.

        xi : float
            Focusing parameter.

        Returns
        -------
        ndarray
            Efficiency curve.
        """

        v_integral = np.vectorize(
            lambda s:
            self.h_integral(
                s,
                xi
            )
        )

        return v_integral(
            vetor_sigma
        )

    # =========================================================================
    # GUI CALLBACKS
    # =========================================================================

    def atualizar(
            self,
            val):
        """
        Callback executed whenever a slider value changes.
        """

        # ---------------------------------------------------------------------
        # Read current slider values
        # ---------------------------------------------------------------------

        xi_atual = self.slider_xi.val
        sigma_atual = self.slider_sigma.val

        # ---------------------------------------------------------------------
        # Recalculate entire curve for the selected xi
        # ---------------------------------------------------------------------

        novos_h = self.calcular_curva_h(
            self.sigma_range,
            xi_atual
        )

        self.linha.set_ydata(
            novos_h
        )

        # ---------------------------------------------------------------------
        # Compute efficiency at selected point
        # ---------------------------------------------------------------------

        h_ponto = self.h_integral(
            sigma_atual,
            xi_atual
        )

        # ---------------------------------------------------------------------
        # Update red marker
        # ---------------------------------------------------------------------

        self.ponto.set_data(
            [sigma_atual],
            [h_ponto]
        )

        # ---------------------------------------------------------------------
        # Update information panel
        # ---------------------------------------------------------------------

        texto = (

            f"--- Leituras Atuais ---\n"
            f"Focalização ($\\xi$): {xi_atual:.2f}\n"
            f"Phase Mismatch ($\\sigma$): {sigma_atual:.2f}\n"
            f"Eficiência (h): {h_ponto:.4f}\n\n"

            f"--- Referência Teórica ---\n"
            f"Ótimo Boyd-Kleinman:\n"
            f"$\\xi$ = {self.xi_opt:.2f}\n"
            f"$\\sigma$ = {self.sigma_opt:.2f}\n\n"

            f"--- Física (Fase de Gouy) ---\n"
            f"A defasagem geométrica do feixe\n"
            f"através do foco introduz uma\n"
            f"rotação de fase acumulada.\n"
            f"Isso desloca o máximo de\n"
            f"eficiência para $\\sigma > 0$,\n"
            f"compensando parcialmente a\n"
            f"perda de coerência macroscópica."
        )

        self.texto_info.set_text(
            texto
        )

        # ---------------------------------------------------------------------
        # Efficient canvas redraw
        # ---------------------------------------------------------------------

        self.fig.canvas.draw_idle()

    # =========================================================================
    # BUTTON CALLBACKS
    # =========================================================================

    def resetar(
            self,
            event):
        """
        Restore theoretical optimum values.
        """

        self.slider_xi.reset()
        self.slider_sigma.reset()

        print(
            "\nParâmetros restaurados "
            "para o ótimo Boyd-Kleinman."
        )

    def exportar(
            self,
            event):
        """
        Export current simulator state.
        """

        export_figure(
            self.fig
        )

        print(
            "Visualização atual exportada com sucesso."
        )


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':

    print(
        "\n"
        "=========================================\n"
        " Interactive Boyd-Kleinman Simulator\n"
        "=========================================\n"
    )

    print(
        "Controles disponíveis:\n"
        "  • Slider ξ  : Focalização\n"
        "  • Slider σ  : Phase Mismatch\n"
        "  • Export    : Salvar PDF/SVG/PNG\n"
        "  • Reset     : Retornar ao ótimo teórico\n"
    )

    simulador = SimuladorBoydKleinman()

    plt.show()