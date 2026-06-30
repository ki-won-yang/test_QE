"""세 물질 band 비교 — 각자의 고대칭 k-path로."""
import matplotlib.pyplot as plt, numpy as np, os, re
MATS=[("graphene","#27ae60","semimetal"),("Al","#c0392b","metal"),("Si","#2980b9","semiconductor")]
def read_fermi(mat):
    for cand in (f"../2_scf/{mat}.scf.out",):
        if os.path.exists(cand):
            ef=None
            for line in open(cand):
                if "Fermi energy" in line:
                    ef=float(re.search(r"(-?\d+\.\d+)",line).group(1))
                elif "highest occupied" in line:
                    n=re.findall(r"(-?\d+\.\d+)",line)
                    if n: ef=float(n[-1])
            return ef
    return None
def load_gnu(mat):
    f=f"{mat}.bands.dat.gnu"
    if not os.path.exists(f): return None
    data=np.loadtxt(f)
    return data
fig,axes=plt.subplots(1,3,figsize=(14,5),sharey=True)
for ax,(mat,c,kind) in zip(axes,MATS):
    d=load_gnu(mat)
    if d is None:
        ax.text(0.5,0.5,f"{mat}.bands.dat.gnu 없음\n(run_all.sh 먼저)",ha="center",va="center",
                transform=ax.transAxes,color="gray"); ax.set_title(f"{mat} ({kind})"); continue
    ef=read_fermi(mat) or 0.0
    k=d[:,0]; e=d[:,1]-ef
    # gnu 포맷은 band별로 빈 줄로 분리 → 끊어 그리기
    breaks=np.where(np.diff(k)<0)[0]+1
    segs=np.split(np.column_stack([k,e]),breaks)
    for s in segs: ax.plot(s[:,0],s[:,1],color=c,lw=0.8)
    ax.axhline(0,color="k",ls="--",lw=1)
    ax.set_title(f"{mat} ({kind})"); ax.set_xlabel("k-path")
    ax.set_ylim(-8,8); ax.grid(ls="--",alpha=0.4)
axes[0].set_ylabel("E - E_F (eV)")
fig.suptitle("Band structure — metal(cross E_F) / semiconductor(gap) / semimetal(Dirac)")
plt.tight_layout(); plt.savefig("bands_compare.png",dpi=150); print("저장: bands_compare.png")
