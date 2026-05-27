"""
[실습 1] SCF 에너지 수렴 시각화
"""

import matplotlib.pyplot as plt
import re


def plot_convergence(filename="scf.out"):
    energies = []
    with open(filename, "r") as f:
        for line in f:
            if "total energy" in line and "=" in line and "Ry" in line:
                match = re.search(r"=\s+(-?\d+\.\d+)", line)
                if match:
                    energies.append(float(match.group(1)))

    if not energies:
        print("⚠️  scf.out에서 에너지 데이터를 찾을 수 없습니다.")
        return

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(energies) + 1), energies, "o-", color="#2c3e50")
    plt.title("SCF Energy Convergence (Graphene)", fontsize=14)
    plt.xlabel("Iteration Step", fontsize=12)
    plt.ylabel("Total Energy (Ry)", fontsize=12)
    plt.xticks(range(1, len(energies) + 1))
    plt.grid(True, linestyle="--")
    plt.tight_layout()
    plt.savefig("scf_convergence.png", dpi=150)
    print(f"이미지 저장 완료: scf_convergence.png (총 {len(energies)} 단계)")


if __name__ == "__main__":
    plot_convergence()
