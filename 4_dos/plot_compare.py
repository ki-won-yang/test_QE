"""세 물질 DOS 비교 — E_F에서의 DOS가 전도성을 가른다."""
import matplotlib.pyplot as plt, numpy as np, re, os
MATS=[("graphene","#27ae60","semimetal"),("Al","#c0392b","metal"),("Si","#2980b9","semiconductor")]
def load(mat):
    f = f"{mat}.dos"
    if not os.path.exists(f): 
        return None, None, None
    
    ef = None
    E, d = [], []
    
    with open(f) as fh:
        for line in fh:
            # 1. 파일 전체를 돌면서 EFermi 찾기
            if ef is None:
                # EFermi가 파일 중간이나 다른 형태로 있을 수 있음
                m = re.search(r"EFermi\s*=\s*(-?\d+\.\d+)", line)
                if m:
                    ef = float(m.group(1))
            
            # 2. 데이터 파싱
            p = line.split()
            if len(p) >= 2:
                try:
                    E.append(float(p[0]))
                    d.append(float(p[1]))
                except ValueError:
                    pass
    
    # 페르미 에너지를 끝내 못 찾았을 경우 디버깅용 경고 출력
    if ef is None:
        print(f"[경고] {mat}.dos 파일에서 EFermi를 찾지 못했습니다! E_F를 0.0으로 가정합니다.")
        ef = 0.0
        
    return np.array(E) - ef, np.array(d), ef
fig,axes=plt.subplots(3,1,figsize=(7,9),sharex=True)
for ax,(mat,c,kind) in zip(axes,MATS):
    E,d,ef=load(mat)
    if E is None:
        ax.text(0.5,0.5,f"{mat}.dos 없음 (run_all.sh 먼저)",ha="center",va="center",
                transform=ax.transAxes,color="gray"); ax.set_ylabel("DOS"); continue
    ax.plot(E,d,color=c,lw=1.4); ax.fill_between(E,d,alpha=0.3,color=c)
    ax.axvline(0,color="k",ls="--",lw=1)
    ax.set_title(f"{mat} ({kind})",loc="left"); ax.set_ylabel("DOS")
    ax.set_xlim(-12, 8)
    
    # X축 -12 ~ 8 eV 범위 안의 데이터만 걸러내기
    mask = (E >= -12) & (E <= 8)
    if np.any(mask):
        max_y = np.max(d[mask])
        ax.set_ylim(0, max_y * 1.1)  # 해당 구간 최댓값의 10% 여유를 두고 Y축 설정
    else:
        ax.set_ylim(bottom=0)
        
    ax.grid(ls="--", alpha=0.4)
axes[-1].set_xlabel("E - E_F (eV)")
fig.suptitle("DOS comparison — E_F: metal(finite) / semiconductor(gap) / semimetal(V)")
plt.tight_layout(rect=[0,0,1,0.97]); plt.savefig("dos_compare.png",dpi=150); print("저장: dos_compare.png")
