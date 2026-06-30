"""세 물질 relax 수렴 비교 (total energy)."""
import matplotlib.pyplot as plt, re
MATS=[("graphene","#27ae60","semimetal"),("Al","#c0392b","metal"),("Si","#2980b9","semiconductor")]
fig,axes=plt.subplots(1,3,figsize=(13,4))
for ax,(mat,c,kind) in zip(axes,MATS):
    E=[]
    try:
        for line in open(f"{mat}.re.out"):
            if "total energy" in line and "=" in line and "Ry" in line:
                m=re.search(r"=\s+(-?\d+\.\d+)",line)
                if m:E.append(float(m.group(1)))
    except FileNotFoundError:
        ax.text(0.5,0.5,f"{mat}.re.out 없음",ha="center",transform=ax.transAxes,color="gray")
        ax.set_title(f"{mat} ({kind})"); continue
    if E: ax.plot(range(1,len(E)+1),E,"o-",color=c)
    ax.set_title(f"{mat} ({kind})"); ax.set_xlabel("step"); ax.set_ylabel("E (Ry)")
    ax.grid(ls="--",alpha=0.5)
fig.suptitle("Relax energy convergence")
plt.tight_layout(); plt.savefig("relax_compare.png",dpi=150); print("저장: relax_compare.png")
