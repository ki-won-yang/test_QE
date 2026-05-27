#!/usr/bin/env python3
import argparse
import csv
import math
import re
from pathlib import Path


def parse_stress(output_path):
    stress_header = re.compile(
        r"total\s+stress\s+\(Ry/bohr\*\*3\)\s+\(kbar\)\s+P=\s*"
        r"([-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?)"
    )
    cell_gradient = re.compile(
        r"Cell gradient error\s*=\s*([-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?)\s*kbar"
    )

    pressures = []
    stress_matrices = []
    cell_gradient_errors = []

    lines = output_path.read_text(encoding="utf-8", errors="replace").splitlines()
    idx = 0
    while idx < len(lines):
        header_match = stress_header.search(lines[idx])
        if header_match:
            pressure = float(header_match.group(1).replace("D", "E").replace("d", "e"))
            matrix = []
            for offset in range(1, 4):
                values = [
                    float(value.replace("D", "E").replace("d", "e"))
                    for value in re.findall(
                        r"[-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?",
                        lines[idx + offset],
                    )
                ]
                if len(values) < 6:
                    raise ValueError(f"Could not parse stress row near line {idx + offset + 1}")
                matrix.append(values[-3:])

            pressures.append(pressure)
            stress_matrices.append(matrix)
            idx += 4
            continue

        gradient_match = cell_gradient.search(lines[idx])
        if gradient_match:
            value = float(gradient_match.group(1).replace("D", "E").replace("d", "e"))
            cell_gradient_errors.append(value)

        idx += 1

    return pressures, stress_matrices, cell_gradient_errors


def stress_norm(matrix):
    return math.sqrt(sum(value * value for row in matrix for value in row))


def in_plane_stress_norm(matrix):
    return math.sqrt(
        matrix[0][0] ** 2
        + matrix[1][1] ** 2
        + matrix[0][1] ** 2
        + matrix[1][0] ** 2
    )


def write_csv(csv_path, pressures, matrices, cell_gradient_errors):
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "iteration",
                "pressure_kbar",
                "stress_norm_kbar",
                "in_plane_stress_norm_kbar",
                "sigma_xx_kbar",
                "sigma_yy_kbar",
                "sigma_zz_kbar",
                "sigma_xy_kbar",
                "sigma_xz_kbar",
                "sigma_yz_kbar",
                "cell_gradient_error_kbar",
            ]
        )
        for idx, (pressure, matrix) in enumerate(zip(pressures, matrices), start=1):
            cell_error = (
                cell_gradient_errors[idx - 1]
                if idx - 1 < len(cell_gradient_errors)
                else ""
            )
            writer.writerow(
                [
                    idx,
                    pressure,
                    stress_norm(matrix),
                    in_plane_stress_norm(matrix),
                    matrix[0][0],
                    matrix[1][1],
                    matrix[2][2],
                    matrix[0][1],
                    matrix[0][2],
                    matrix[1][2],
                    cell_error,
                ]
            )


def plot_stress(png_path, pressures, matrices, cell_gradient_errors, title, show):
    import matplotlib.pyplot as plt

    iterations = list(range(1, len(pressures) + 1))
    pressure_abs = [abs(value) for value in pressures]
    total_norm = [stress_norm(matrix) for matrix in matrices]
    in_plane_norm = [in_plane_stress_norm(matrix) for matrix in matrices]

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(7.6, 6.2),
        dpi=160,
        sharex=True,
        gridspec_kw={"height_ratios": [1.1, 1.0]},
    )

    ax_top.semilogy(
        iterations,
        pressure_abs,
        marker="o",
        linewidth=1.6,
        markersize=4,
        label="|Pressure|",
    )
    ax_top.semilogy(
        iterations,
        total_norm,
        marker="s",
        linewidth=1.4,
        markersize=3,
        label="Stress tensor norm",
    )
    ax_top.semilogy(
        iterations,
        in_plane_norm,
        marker="^",
        linewidth=1.4,
        markersize=3,
        label="In-plane stress norm",
    )

    if cell_gradient_errors:
        ax_top.semilogy(
            iterations[: len(cell_gradient_errors)],
            cell_gradient_errors,
            marker="x",
            linewidth=1.4,
            markersize=4,
            label="Cell gradient error",
        )

    ax_top.set_ylabel("Stress scale (kbar)")
    ax_top.set_title(title)
    ax_top.grid(True, which="both", alpha=0.3)
    ax_top.legend()

    ax_bottom.plot(
        iterations,
        [matrix[0][0] for matrix in matrices],
        marker="o",
        linewidth=1.4,
        markersize=3,
        label="sigma_xx",
    )
    ax_bottom.plot(
        iterations,
        [matrix[1][1] for matrix in matrices],
        marker="s",
        linewidth=1.4,
        markersize=3,
        label="sigma_yy",
    )
    ax_bottom.plot(
        iterations,
        [matrix[2][2] for matrix in matrices],
        marker="^",
        linewidth=1.4,
        markersize=3,
        label="sigma_zz",
    )
    ax_bottom.plot(
        iterations,
        [matrix[0][1] for matrix in matrices],
        marker="x",
        linewidth=1.4,
        markersize=4,
        label="sigma_xy",
    )
    ax_bottom.axhline(0.0, color="black", linewidth=0.8, alpha=0.5)
    ax_bottom.set_xlabel("Stress evaluation / ionic step")
    ax_bottom.set_ylabel("Component (kbar)")
    ax_bottom.grid(True, alpha=0.3)
    ax_bottom.legend(ncol=2)

    fig.tight_layout()
    fig.savefig(png_path, bbox_inches="tight")

    if show:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot Quantum ESPRESSO stress convergence from a pw.x vc-relax output file."
    )
    parser.add_argument("output", nargs="?", default="vc.out", help="QE vc-relax output file")
    parser.add_argument("--png", default=None, help="output PNG path")
    parser.add_argument("--csv", default=None, help="optional output CSV path")
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="save the PNG without opening an interactive plot window",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    if not output_path.exists():
        raise SystemExit(f"Cannot find output file: {output_path}")

    pressures, matrices, cell_gradient_errors = parse_stress(output_path)
    if not matrices:
        raise SystemExit(f"No stress tensor blocks were found in {output_path}")

    png_path = Path(args.png) if args.png else output_path.with_suffix(".stress.png")
    csv_path = Path(args.csv) if args.csv else None

    if csv_path is not None:
        write_csv(csv_path, pressures, matrices, cell_gradient_errors)

    plot_stress(
        png_path,
        pressures,
        matrices,
        cell_gradient_errors,
        f"{output_path.name} stress convergence",
        not args.no_show,
    )

    final_matrix = matrices[-1]
    print(f"Parsed {len(matrices)} stress blocks from {output_path}")
    print(f"Initial pressure: {pressures[0]:.6f} kbar")
    print(f"Final pressure: {pressures[-1]:.6f} kbar")
    print(f"Final stress norm: {stress_norm(final_matrix):.6e} kbar")
    print(f"Final in-plane stress norm: {in_plane_stress_norm(final_matrix):.6e} kbar")
    if cell_gradient_errors:
        print(f"Final cell gradient error: {cell_gradient_errors[-1]:.6e} kbar")
    print(f"Saved plot: {png_path}")
    if csv_path is not None:
        print(f"Saved data: {csv_path}")


if __name__ == "__main__":
    main()
