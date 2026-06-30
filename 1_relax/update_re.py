"""vc-relax 출력의 'final coordinates'를 relax 입력에 반영."""
import sys, re as RE
vcout, reff = sys.argv[1], sys.argv[2]
txt = open(vcout).read()
m = RE.search(r"Begin final coordinates(.*?)End final coordinates", txt, RE.S)
if not m:
    print(f"  [경고] {vcout}에 final coordinates 없음 — re.in 초기값 유지"); sys.exit(0)
blk = m.group(1)
cell = RE.search(r"(CELL_PARAMETERS.*?)(?=ATOMIC_POSITIONS)", blk, RE.S)
pos  = RE.search(r"(ATOMIC_POSITIONS.*)", blk, RE.S)
src = open(reff).read()
if cell:
    src = RE.sub(r"CELL_PARAMETERS.*?(?=ATOMIC_POSITIONS)", cell.group(1), src, flags=RE.S)
if pos:
    src = RE.sub(r"ATOMIC_POSITIONS.*?(?=K_POINTS)", pos.group(1).rstrip()+"\n", src, flags=RE.S)
open(reff,"w").write(src)
print(f"  {reff} ← {vcout} 최종구조 반영")
