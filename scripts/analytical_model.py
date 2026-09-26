"""
analytical_model.py

Analytical model for a Multi-Layer Insulation (MLI) blanket, translating the
radiative behavior of a stack of N reflective shields into an equivalent
thermal resistance usable in a pure-conduction (Fourier) model.

Reproduces the relations derived in the "Approche Analytique du Transfert
Radiatif dans la MLI" chapter:

    eps_eff  ~= eps_feuille / (2N)                      (N >> 1, eps_feuille << 1)
    k_eff     = (e_couche * eps_feuille * sigma / 2)
                * (T_int + T_ext) * (T_int**2 + T_ext**2)
    R_s       = e / k_eff = 2N / (eps_feuille * sigma * (T_int+T_ext) * (T_int**2+T_ext**2))
    Q/A       = (T_int - T_ext) / R_s
    m_MLI(N)  = N * areal_mass * A_total

Run directly to regenerate data/raw/comsol_sweep_results.csv-equivalent
analytical table and data/processed/mass_vs_performance.csv.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

SIGMA = 5.67e-8  # Stefan-Boltzmann constant, W/(m^2.K^4)


@dataclass
class MLIParameters:
    """Physical parameters of the MLI stack and boundary temperatures."""

    eps_feuille: float = 0.03       # emissivity of a single aluminized shield
    e_couche: float = 0.05e-3       # thickness of a single layer, m (0.05 mm)
    T_int: float = 293.15           # habitat-side temperature, K
    T_ext: float = 4.0              # space-side temperature, K
    areal_mass: float = 0.030       # mass per unit area per layer, kg/m^2 (30 g/m^2)
    A_total: float = 138.0          # total habitat surface area, m^2


def effective_emissivity(N: int, params: MLIParameters) -> float:
    """Effective emissivity of an N-layer stack (exact formula)."""
    return 1.0 / ((N + 1) * (2.0 / params.eps_feuille - 1.0))


def effective_emissivity_approx(N: int, params: MLIParameters) -> float:
    """Simplified effective emissivity, valid for eps_feuille << 1 and N >> 1."""
    return params.eps_feuille / (2.0 * N)


def k_eff(params: MLIParameters) -> float:
    """Equivalent (fictitious) thermal conductivity of the MLI stack, W/(m.K).

    Independent of N: the N-dependence of the flux comes entirely from the
    total thickness e = N * e_couche in R_s below.
    """
    return (
        params.e_couche * params.eps_feuille * SIGMA / 2.0
        * (params.T_int + params.T_ext)
        * (params.T_int**2 + params.T_ext**2)
    )


def equivalent_resistance(N: int, params: MLIParameters) -> float:
    """Equivalent areal thermal resistance R_s (K.m^2/W) for N layers."""
    return (2.0 * N) / (
        params.eps_feuille * SIGMA
        * (params.T_int + params.T_ext)
        * (params.T_int**2 + params.T_ext**2)
    )


def heat_flux_density(N: int, params: MLIParameters) -> float:
    """Heat flux per unit area Q/A (W/m^2) through the MLI for N layers."""
    R_s = equivalent_resistance(N, params)
    return (params.T_int - params.T_ext) / R_s


def heat_flux_total(N: int, params: MLIParameters) -> float:
    """Total heat flux Q (W) through the full habitat surface for N layers."""
    return heat_flux_density(N, params) * params.A_total


def mli_mass(N: int, params: MLIParameters) -> float:
    """Total MLI mass (kg) added to the habitat for N layers."""
    return N * params.areal_mass * params.A_total


def build_table(N_values, params: MLIParameters | None = None):
    """Return a list of dict rows: N, eps_eff, eps_eff_approx, Q (W), mass (kg)."""
    params = params or MLIParameters()
    rows = []
    for N in N_values:
        rows.append(
            {
                "N": N,
                "eps_eff": effective_emissivity(N, params),
                "eps_eff_approx": effective_emissivity_approx(N, params),
                "R_s": equivalent_resistance(N, params),
                "Q_W": heat_flux_total(N, params),
                "mass_kg": mli_mass(N, params),
            }
        )
    return rows


def write_csv(rows, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    N_values = [5, 10, 15, 20, 25, 30, 40, 50]
    params = MLIParameters()

    rows = build_table(N_values, params)

    print(f"{'N':>4} {'eps_eff':>12} {'R_s (K.m2/W)':>14} {'Q (W)':>10} {'mass (kg)':>10}")
    for r in rows:
        print(
            f"{r['N']:>4} {r['eps_eff']:>12.6e} {r['R_s']:>14.2f} "
            f"{r['Q_W']:>10.2f} {r['mass_kg']:>10.1f}"
        )

    out_dir = Path(__file__).resolve().parent.parent / "data"
    write_csv(rows, out_dir / "processed" / "analytical_results.csv")
    print(f"\nSaved: {out_dir / 'processed' / 'analytical_results.csv'}")
