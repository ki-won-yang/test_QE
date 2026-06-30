"""세 물질 DOS 비교 — E_F에서의 DOS가 전도성을 가른다."""
import matplotlib.pyplot as plt, numpy as np, re, os
MATS=[("graphene","#27ae60","semimetal"),("Al","#c0392b","metal"),("Si","#2980b9","semiconductor")]
def load(mat):
    f=f"{mat}.dos"
    if not os.path.exists(f): return None,None,None
    ef=None
    with open(f) as fh:
        h=fh.readline(); m=re.search(r"EFermi\s*=\s*(-?\d+\.\d+)",h)
        ef=float(m.group(1)) if m else 0.0
        E,d=[],[]
        for line in fh:
            p=line.split()
            if len(p)>=2:
                try:E.append(float(p[0]));d.append(float(p[1]))
                except:pass
    return np.array(E)-ef,np.array(d),ef
fig,axes=plt.subplots(3,1,figsize=(7,9),sharex=True)
for ax,(mat,c,kind) in zip(axes,MATS):
    E,d,ef=load(mat)
    if E is None:
        ax.text(0.5,0.5,f"{mat}.dos 없음 (run_all.sh 먼저)",ha="center",va="center",
                transform=ax.transAxes,color="gray"); ax.set_ylabel("DOS"); continue
    ax.plot(E,d,color=c,lw=1.4); ax.fill_between(E,d,alpha=0.3,color=c)
    ax.axvline(0,color="k",ls="--",lw=1)
    ax.set_title(f"{mat} ({kind})",loc="left"); ax.set_ylabel("DOS")
    ax.set_xlim(-12,8); ax.set_ylim(bottom=0); ax.grid(ls="--",alpha=0.4)
axes[-1].set_xlabel("E - E_F (eV)")
fig.suptitle("DOS comparison — E_F: metal(finite) / semiconductor(gap) / semimetal(V)")
plt.tight_layout(rect=[0,0,1,0.97]); plt.savefig("dos_compare.png",dpi=150); print("저장: dos_compare.png")
