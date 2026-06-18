#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_U_VALUES = ["0.0", "1.5", "3.0", "4.5"]


def read_gnu_bands(path):
    bands = []
    current_k = []
    current_e = []

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                if current_k:
                    bands.append((np.array(current_k), np.array(current_e)))
                    current_k = []
                    current_e = []
                continue

            parts = stripped.split()
            if len(parts) < 2:
                continue
            current_k.append(float(parts[0]))
            current_e.append(float(parts[1]))

    if current_k:
        bands.append((np.array(current_k), np.array(current_e)))

    return bands


def read_fermi_energy(path):
    if not path.exists():
        return None

    pattern = re.compile(r"the Fermi energy is\s+([-+]?\d+(?:\.\d*)?)\s+ev", re.I)
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = pattern.search(line)
            if match:
                return float(match.group(1))
    return None


def high_symmetry_ticks(k_values):
    unique = [float(k_values[0])]
    for value in k_values[1:]:
        value = float(value)
        if abs(value - unique[-1]) > 1.0e-8:
            unique.append(value)

    if len(unique) < 2:
        return unique, [""] * len(unique)

    labels = ["L", "Gamma", "X", "U|K", "Gamma"]
    if len(unique) >= len(labels):
        indices = np.linspace(0, len(unique) - 1, len(labels), dtype=int)
        ticks = [unique[i] for i in indices]
        return ticks, labels

    return unique, [str(i + 1) for i in range(len(unique))]


def plot_comparison(files, labels, fermi_values, output, show, energy_window):
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    fig, ax = plt.subplots(figsize=(7.2, 6.0), dpi=160)

    tick_source = None
    plotted_labels = set()

    for idx, (path, label, fermi) in enumerate(zip(files, labels, fermi_values)):
        bands = read_gnu_bands(path)
        if not bands:
            print(f"Warning: no band data found in {path}")
            continue

        color = colors[idx % len(colors)]
        if tick_source is None:
            tick_source = bands[0][0]

        shift = fermi if fermi is not None else 0.0
        if fermi is None:
            print(f"Warning: Fermi energy not found for {label}; plotting without shift")

        for k_values, energies in bands:
            plot_label = label if label not in plotted_labels else None
            ax.plot(
                k_values,
                energies - shift,
                color=color,
                linewidth=1.0,
                alpha=0.78,
                label=plot_label,
            )
            plotted_labels.add(label)

    ax.axhline(0.0, color="black", linestyle="--", linewidth=0.8, alpha=0.75)

    if tick_source is not None:
        ticks, tick_labels = high_symmetry_ticks(tick_source)
        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels)
        for tick in ticks[1:-1]:
            ax.axvline(tick, color="gray", linestyle=":", linewidth=0.6, alpha=0.7)
        ax.set_xlim(float(tick_source[0]), float(tick_source[-1]))

    if energy_window is not None:
        ax.set_ylim(energy_window)

    ax.set_xlabel("k-path")
    ax.set_ylabel("Energy - E_F (eV)")
    ax.set_title("MoS2 band structure comparison by Hubbard U")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(title="Hubbard U", loc="best")

    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")

    if show:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Compare Quantum ESPRESSO band structures for several Hubbard U values."
    )
    parser.add_argument(
        "--u-values",
        nargs="+",
        default=DEFAULT_U_VALUES,
        help="U values to plot, matching MoS2_bands_U<value>.dat.gnu",
    )
    parser.add_argument("--prefix", default="MoS2", help="QE prefix used in file names")
    parser.add_argument(
        "--scf-dir",
        default="../5_scf_U",
        help="directory containing 5_scf_U/scf_U<value>.out files used for Fermi energies",
    )
    parser.add_argument("--output", default="MoS2_bands_U_compare.png", help="output PNG path")
    parser.add_argument(
        "--emin",
        type=float,
        default=-3.0,
        help="minimum y-axis value in eV relative to Fermi level",
    )
    parser.add_argument(
        "--emax",
        type=float,
        default=3.0,
        help="maximum y-axis value in eV relative to Fermi level",
    )
    parser.add_argument(
        "--no-fermi-shift",
        action="store_true",
        help="plot raw band energies instead of subtracting Fermi energy",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="save the PNG without opening an interactive plot window",
    )
    args = parser.parse_args()

    files = []
    labels = []
    fermi_values = []

    for u_value in args.u_values:
        tag = f"U{u_value}"
        gnu_path = Path(f"{args.prefix}_bands_{tag}.dat.gnu")
        scf_out_path = Path(args.scf_dir) / f"scf_{tag}.out"
        if not gnu_path.exists():
            raise SystemExit(f"Cannot find band file: {gnu_path}")

        files.append(gnu_path)
        labels.append(f"U={u_value} eV")
        fermi_values.append(
            None if args.no_fermi_shift else read_fermi_energy(scf_out_path)
        )

    energy_window = None
    if args.emin is not None and args.emax is not None:
        energy_window = (args.emin, args.emax)

    plot_comparison(
        files,
        labels,
        fermi_values,
        Path(args.output),
        not args.no_show,
        energy_window,
    )

    print(f"Saved comparison plot: {args.output}")


if __name__ == "__main__":
    main()
