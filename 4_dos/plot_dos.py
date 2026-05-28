"""
[실습 3] Graphene DOS / PDOS 시각화
"""

import matplotlib.pyplot as plt
import numpy as np
import glob
import re


def get_fermi_energy(scf_output="../2_scf/scf.out"):
    """scf.out에서 페르미 에너지(eV)를 추출합니다."""
    with open(scf_output, "r") as f:
        for line in f:
            if "the Fermi energy is" in line:
                return float(re.search(r"(-?\d+\.\d+)", line).group(1))
    print("⚠️  페르미 에너지를 찾지 못했습니다. E_F = 0 으로 설정합니다.")
    return 0.0


def plot_dos(dosfile="graphene_dos.dat", scf_output="../2_scf/scf.out"):
    """Total DOS를 그립니다."""
    e_fermi = get_fermi_energy(scf_output)

    data = np.loadtxt(dosfile)
    energy = data[:, 0] - e_fermi
    dos = data[:, 1]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(energy, dos, color="#2c3e50", linewidth=1.2)
    ax.axvline(0, color="#e74c3c", linestyle="--", linewidth=0.8, label="$E_F$")
    ax.fill_between(energy, dos, alpha=0.15, color="#2c3e50")

    ax.set_xlim(-25, 10)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Energy − $E_F$ (eV)", fontsize=12)
    ax.set_ylabel("DOS (states/eV)", fontsize=12)
    ax.set_title("Graphene Total DOS", fontsize=14)
    ax.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig("dos_total.png", dpi=150)
    print("이미지 저장 완료: dos_total.png")


def plot_pdos(scf_output="../2_scf/scf.out"):
    """PDOS를 궤도별(s, p)로 분리하여 그립니다."""
    e_fermi = get_fermi_energy(scf_output)

    pdos_files = sorted(glob.glob("graphene_pdos.pdos_atm*"))
    if not pdos_files:
        print("⚠️  PDOS 파일을 찾을 수 없습니다. projwfc.x 를 먼저 실행하세요.")
        return

    fig, ax = plt.subplots(figsize=(6, 5))
    colors = {"s": "#3498db", "p": "#e74c3c", "d": "#2ecc71"}

    orbital_dos = {}
    energy = None
    for f in pdos_files:
        match = re.search(r"wfc#\d+\((\w+)\)", f)
        if not match:
            continue
        orb = match.group(1)

        data = np.loadtxt(f)
        if energy is None:
            energy = data[:, 0] - e_fermi
        ldos = data[:, 1]

        if orb not in orbital_dos:
            orbital_dos[orb] = np.zeros_like(ldos)
        orbital_dos[orb] += ldos

    for orb, dos in orbital_dos.items():
        c = colors.get(orb, "#7f8c8d")
        ax.plot(energy, dos, color=c, linewidth=1.2, label=f"C-{orb}")
        ax.fill_between(energy, dos, alpha=0.1, color=c)

    ax.axvline(0, color="black", linestyle="--", linewidth=0.8, label="$E_F$")
    ax.set_xlim(-25, 10)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Energy − $E_F$ (eV)", fontsize=12)
    ax.set_ylabel("PDOS (states/eV)", fontsize=12)
    ax.set_title("Graphene Projected DOS (s, p orbitals)", fontsize=14)
    ax.legend(fontsize=11)

    plt.tight_layout()
    plt.savefig("pdos_orbital.png", dpi=150)
    print("이미지 저장 완료: pdos_orbital.png")


if __name__ == "__main__":
    plot_dos()
    plot_pdos()
