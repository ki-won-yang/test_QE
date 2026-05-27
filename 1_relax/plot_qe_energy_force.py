#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path


RY_TO_EV = 13.605693122994
RY_PER_AU_TO_EV_PER_ANG = 25.71104309541616


def parse_ionic_energies(output_path):
    pattern = re.compile(
        r"^\s*!\s+total energy\s+=\s+([-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?)\s+Ry"
    )
    energies = []

    with output_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = pattern.search(line)
            if match:
                energies.append(float(match.group(1).replace("D", "E").replace("d", "e")))

    return energies


def parse_forces(output_path):
    pattern = re.compile(
        r"Total force\s*=\s*([-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?)"
        r"\s+Total SCF correction\s*=\s*([-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?)"
    )
    forces = []
    scf_corrections = []

    with output_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = pattern.search(line)
            if match:
                forces.append(float(match.group(1).replace("D", "E").replace("d", "e")))
                scf_corrections.append(
                    float(match.group(2).replace("D", "E").replace("d", "e"))
                )

    return forces, scf_corrections


def write_csv(csv_path, energies, forces, scf_corrections):
    count = max(len(energies), len(forces))
    first_energy = energies[0] if energies else None

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "iteration",
                "total_energy_Ry",
                "delta_energy_eV",
                "total_force_Ry_per_au",
                "total_force_eV_per_Ang",
                "scf_correction_Ry_per_au",
                "scf_correction_eV_per_Ang",
            ]
        )
        for idx in range(count):
            energy = energies[idx] if idx < len(energies) else ""
            force = forces[idx] if idx < len(forces) else ""
            correction = scf_corrections[idx] if idx < len(scf_corrections) else ""
            delta_energy = (
                (energy - first_energy) * RY_TO_EV
                if first_energy is not None and energy != ""
                else ""
            )
            writer.writerow(
                [
                    idx + 1,
                    energy,
                    delta_energy,
                    force,
                    force * RY_PER_AU_TO_EV_PER_ANG if force != "" else "",
                    correction,
                    correction * RY_PER_AU_TO_EV_PER_ANG if correction != "" else "",
                ]
            )


def positive_log_values(values, floor):
    return [value if value > 0 else floor for value in values]


def plot_energy_force(
    png_path,
    energies,
    forces,
    scf_corrections,
    threshold,
    title,
    show,
):
    import matplotlib.pyplot as plt

    fig, (ax_energy, ax_force) = plt.subplots(
        2,
        1,
        figsize=(7.6, 6.2),
        dpi=160,
        sharex=False,
        gridspec_kw={"height_ratios": [1.0, 1.1]},
    )

    energy_iterations = list(range(1, len(energies) + 1))
    delta_energy_ev = [(energy - energies[0]) * RY_TO_EV for energy in energies]

    ax_energy.plot(
        energy_iterations,
        energies,
        marker="o",
        linewidth=1.8,
        markersize=4,
        label="Total energy",
    )
    ax_energy.set_ylabel("Total energy (Ry)")
    ax_energy.set_title(title)
    ax_energy.grid(True, alpha=0.3)

    ax_energy_delta = ax_energy.twinx()
    ax_energy_delta.plot(
        energy_iterations,
        delta_energy_ev,
        color="tab:orange",
        linewidth=1.2,
        alpha=0.75,
        label="Delta energy",
    )
    ax_energy_delta.set_ylabel("Delta from first step (eV)")

    energy_lines, energy_labels = ax_energy.get_legend_handles_labels()
    delta_lines, delta_labels = ax_energy_delta.get_legend_handles_labels()
    ax_energy.legend(energy_lines + delta_lines, energy_labels + delta_labels)

    force_iterations = list(range(1, len(forces) + 1))
    force_ev_ang = [force * RY_PER_AU_TO_EV_PER_ANG for force in forces]
    correction_ev_ang = [
        correction * RY_PER_AU_TO_EV_PER_ANG for correction in scf_corrections
    ]

    positive_values = [value for value in force_ev_ang + correction_ev_ang if value > 0]
    if threshold is not None:
        plot_floor = threshold * RY_PER_AU_TO_EV_PER_ANG * 0.5
    elif positive_values:
        plot_floor = min(positive_values) * 0.5
    else:
        plot_floor = 1.0e-12

    ax_force.semilogy(
        force_iterations,
        positive_log_values(force_ev_ang, plot_floor),
        marker="o",
        linewidth=1.8,
        markersize=4,
        label="Total force",
    )
    ax_force.semilogy(
        force_iterations,
        positive_log_values(correction_ev_ang, plot_floor),
        marker="s",
        linewidth=1.2,
        markersize=3,
        alpha=0.75,
        label="SCF correction",
    )

    if threshold is not None:
        ax_force.axhline(
            threshold * RY_PER_AU_TO_EV_PER_ANG,
            linestyle="--",
            linewidth=1.2,
            color="tab:red",
            label=f"forc_conv_thr = {threshold:g} Ry/au",
        )

    ax_force.set_xlabel("Ionic iteration")
    ax_force.set_ylabel("Force (eV/Angstrom)")
    ax_force.grid(True, which="both", alpha=0.3)
    ax_force.legend()

    if any(value <= 0 for value in force_ev_ang + correction_ev_ang):
        ax_force.text(
            0.02,
            0.03,
            "Zero values are shown below the threshold on this log plot.",
            transform=ax_force.transAxes,
            fontsize=8,
            alpha=0.75,
        )

    fig.tight_layout()
    fig.savefig(png_path, bbox_inches="tight")

    if show:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot Quantum ESPRESSO total energy and force convergence together."
    )
    parser.add_argument("output", nargs="?", default="re.out", help="QE relax output file")
    parser.add_argument("--png", default=None, help="output PNG path")
    parser.add_argument("--csv", default=None, help="optional output CSV path")
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.0e-8,
        help="force convergence threshold in Ry/au; use 0 to hide the line",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="save the PNG without opening an interactive plot window",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    if not output_path.exists():
        raise SystemExit(f"Cannot find output file: {output_path}")

    energies = parse_ionic_energies(output_path)
    forces, scf_corrections = parse_forces(output_path)

    if not energies:
        raise SystemExit(f"No ionic total energy lines were found in {output_path}")
    if not forces:
        raise SystemExit(f"No Total force lines were found in {output_path}")

    png_path = Path(args.png) if args.png else output_path.with_suffix(".energy_force.png")
    csv_path = Path(args.csv) if args.csv else None
    threshold = None if args.threshold == 0 else args.threshold

    if csv_path is not None:
        write_csv(csv_path, energies, forces, scf_corrections)

    plot_energy_force(
        png_path,
        energies,
        forces,
        scf_corrections,
        threshold,
        f"{output_path.name} energy and force convergence",
        not args.no_show,
    )

    print(f"Parsed {len(energies)} energy points from {output_path}")
    print(f"Parsed {len(forces)} force points from {output_path}")
    print(f"Initial energy: {energies[0]:.10f} Ry")
    print(f"Final energy: {energies[-1]:.10f} Ry")
    print(f"Energy change: {(energies[-1] - energies[0]):.10e} Ry")
    print(f"Initial force: {forces[0]:.10e} Ry/au")
    print(f"Final force: {forces[-1]:.10e} Ry/au")
    print(f"Saved plot: {png_path}")
    if csv_path is not None:
        print(f"Saved data: {csv_path}")


if __name__ == "__main__":
    main()
