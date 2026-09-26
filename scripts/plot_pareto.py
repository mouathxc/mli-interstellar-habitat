"""
plot_pareto.py

Builds the mass-vs-performance (Pareto) curve for the MLI blanket: added mass
m_MLI(N) vs heat flux Q(N), and reports the N at which the two curves cross
(a convenient, if not physically rigorous, visual marker for the "point of
diminishing returns" discussed in the report).

Usage:
    python plot_pareto.py
    python plot_pareto.py --out figures/pareto_curve.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from analytical_model import MLIParameters, build_table


def find_crossing(N_values, Q_values, mass_values):
    """Return the N (interpolated) where Q(N) and mass(N) curves cross."""
    Q = np.array(Q_values, dtype=float)
    m = np.array(mass_values, dtype=float)
    diff = Q - m
    sign_changes = np.where(np.diff(np.sign(diff)) != 0)[0]
    if len(sign_changes) == 0:
        return None
    i = sign_changes[0]
    # linear interpolation between N[i] and N[i+1]
    N0, N1 = N_values[i], N_values[i + 1]
    d0, d1 = diff[i], diff[i + 1]
    N_cross = N0 + (N1 - N0) * (-d0) / (d1 - d0)
    return N_cross


def main():
    parser = argparse.ArgumentParser(description="Plot the MLI mass-vs-performance Pareto curve.")
    parser.add_argument(
        "--out", type=Path, default=Path("figures/pareto_curve.png"), help="Output image path"
    )
    args = parser.parse_args()

    N_values = list(range(5, 51))  # fine sweep for a smooth curve
    rows = build_table(N_values, MLIParameters())
    Q_values = [r["Q_W"] for r in rows]
    mass_values = [r["mass_kg"] for r in rows]

    N_cross = find_crossing(N_values, Q_values, mass_values)

    fig, ax1 = plt.subplots(figsize=(7, 5))

    ax1.set_xlabel("Number of MLI layers, N")
    ax1.set_ylabel("Heat flux Q (W)", color="tab:blue")
    ax1.plot(N_values, Q_values, color="tab:blue", linewidth=2, label="Q(N)")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Added MLI mass (kg)", color="tab:red")
    ax2.plot(N_values, mass_values, color="tab:red", linewidth=2, label="mass(N)")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    if N_cross is not None:
        ax1.axvline(N_cross, color="gray", linestyle="--", alpha=0.7)
        ax1.text(
            N_cross + 0.5,
            max(Q_values) * 0.9,
            f"N \u2248 {N_cross:.1f}",
            color="gray",
        )
        print(f"Q(N) and mass(N) curves cross near N = {N_cross:.2f}")

    fig.suptitle("MLI mass vs. thermal performance (Pareto curve)")
    fig.tight_layout()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=200)
    print(f"Saved plot to {args.out}")


if __name__ == "__main__":
    main()
