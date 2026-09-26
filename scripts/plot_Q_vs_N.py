"""
plot_Q_vs_N.py

Plots the heat flux Q (W) crossing the MLI blanket as a function of the
number of layers N, reproducing the "Courbe du flux thermique traversant Q
en fonction du nombre de couches N" figure from the report.

Usage:
    python plot_Q_vs_N.py                       # uses the analytical model
    python plot_Q_vs_N.py --csv path/to/data.csv  # uses a COMSOL export instead

The CSV, if provided, is expected to have at least the columns "N" and "Q_W"
(rename your COMSOL export's columns to match, or edit COLUMN_MAP below).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt

from analytical_model import MLIParameters, build_table

COLUMN_MAP = {"N": "N", "Q": "Q_W"}  # adjust if your CSV uses different headers


def load_from_csv(path: Path):
    N_values, Q_values = [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            N_values.append(float(row[COLUMN_MAP["N"]]))
            Q_values.append(float(row[COLUMN_MAP["Q"]]))
    return N_values, Q_values


def load_from_model():
    N_values = [5, 10, 15, 20, 25, 30, 40, 50]
    rows = build_table(N_values, MLIParameters())
    return [r["N"] for r in rows], [r["Q_W"] for r in rows]


def main():
    parser = argparse.ArgumentParser(description="Plot Q vs N for the MLI blanket.")
    parser.add_argument("--csv", type=Path, default=None, help="Optional COMSOL results CSV")
    parser.add_argument(
        "--out", type=Path, default=Path("figures/Q_vs_N.png"), help="Output image path"
    )
    args = parser.parse_args()

    if args.csv:
        N_values, Q_values = load_from_csv(args.csv)
        label = "COMSOL simulation"
    else:
        N_values, Q_values = load_from_model()
        label = "Analytical model"

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(N_values, Q_values, marker="o", linewidth=2, label=label)
    ax.set_xlabel("Number of MLI layers, N")
    ax.set_ylabel("Heat flux crossing the wall, Q (W)")
    ax.set_title("Heat flux through the MLI vs. number of layers")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=200)
    print(f"Saved plot to {args.out}")


if __name__ == "__main__":
    main()
