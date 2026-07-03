#!/bin/bash
# [실습 4] 세 물질 DOS (SCF 먼저 필요)
set -uo pipefail
# 마스터: 빈 값(직렬) / 노드 slurm: mpirun -np N 이 주입됨
QE_MPIRUN="${QE_MPIRUN:-}"
export OMPI_MCA_pml=ob1; export OMPI_MCA_btl=self,tcp; export OMP_NUM_THREADS=1
if ! command -v pw.x >/dev/null 2>&1 && [ -f "$HOME/miniconda3/bin/activate" ]; then
    source "$HOME/miniconda3/bin/activate"; fi
for MAT in graphene Al Si; do
  if [ ! -d ../tmp_${MAT} ]; then echo "  [경고] ../tmp_${MAT} 없음 → 2_scf를 먼저 실행하세요"; continue; fi
  echo "=== [$MAT] nscf + dos ==="
  pw.x  < ${MAT}.nscf.in > ${MAT}.nscf.out
  $QE_MPIRUN dos.x < ${MAT}.dos.in  > ${MAT}.dos.out
done
echo; echo "비교: python3 plot_compare.py"
