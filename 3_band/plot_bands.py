"""
[실습 2] Graphene Band Structure 시각화
"""

import matplotlib.pyplot as plt
import numpy as np
import re


def get_fermi_energy(scf_output="../2_scf/scf.out"):
    """scf.out에서 페르미 에너지(eV)를 추출합니다."""
    with open(scf_output, "r") as f:
        for line in f:
            if "the Fermi energy is" in line:
                return float(re.search(r"(-?\d+\.\d+)", line).group(1))
    print("⚠️  페르미 에너지를 찾지 못했습니다. E_F = 0 으로 설정합니다.")
    return 0.0


def plot_bands(datafile="graphene_bands.dat.gnu", scf_output="../2_scf/scf.out"):
    e_fermi = get_fermi_energy(scf_output)
    print(f"페르미 에너지: {e_fermi:.4f} eV")

    with open(datafile, "r") as f:
        lines = f.readlines()

    band_data = []
    current_k, current_e = [], []
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            if current_k:
                band_data.append((np.array(current_k), np.array(current_e)))
                current_k, current_e = [], []
        else:
            vals = stripped.split()
            current_k.append(float(vals[0]))
            current_e.append(float(vals[1]))
    if current_k:
        band_data.append((np.array(current_k), np.array(current_e)))

    print(f"밴드 수: {len(band_data)}")

    k_ref = band_data[0][0]
    n_pts = len(k_ref)
    seg_len = n_pts // 3
    tick_positions = [k_ref[0], k_ref[seg_len], k_ref[2 * seg_len], k_ref[-1]]
    tick_labels = ["Γ", "M", "K", "Γ"]

    fig, ax = plt.subplots(figsize=(6, 7))
    for k, e in band_data:
        ax.plot(k, e - e_fermi, color="#2c3e50", linewidth=1.2)

    ax.axhline(0, color="#e74c3c", linestyle="--", linewidth=0.8, label="$E_F$")
    for xp in tick_positions[1:-1]:
        ax.axvline(xp, color="gray", linestyle=":", linewidth=0.5)

    ax.set_xlim(k_ref[0], k_ref[-1])
    ax.set_ylim(-20, 20)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=13)
    ax.set_ylabel("Energy (eV)", fontsize=13)
    ax.set_title("Graphene Band Structure", fontsize=14)
    ax.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig("band_structure.png", dpi=150)
    print("이미지 저장 완료: band_structure.png")


if __name__ == "__main__":
    plot_bands()
