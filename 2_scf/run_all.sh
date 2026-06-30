#!/bin/bash
# [실습 2] 세 물질 SCF
set -uo pipefail
export OMPI_MCA_pml=ob1; export OMPI_MCA_btl=self,tcp; export OMP_NUM_THREADS=1
if ! command -v pw.x >/dev/null 2>&1 && [ -f "$HOME/miniconda3/bin/activate" ]; then
    source "$HOME/miniconda3/bin/activate"; fi
for MAT in graphene Al Si; do
  echo "=== [$MAT] SCF ==="
  mkdir -p ../tmp_${MAT}
  pw.x < ${MAT}.scf.in > ${MAT}.scf.out
  grep -q "convergence has been achieved" ${MAT}.scf.out && echo "  [$MAT] 수렴 OK" || echo "  [$MAT] 수렴 확인 필요"
done
echo; echo "비교: python3 plot_compare.py"
