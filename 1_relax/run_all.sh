#!/bin/bash
# [실습 1] 세 물질 구조 최적화 (vc-relax → relax)
set -uo pipefail
# 마스터: 빈 값(직렬) / 노드 slurm: mpirun -np N 이 주입됨
QE_MPIRUN="${QE_MPIRUN:-}"
export OMPI_MCA_pml=ob1; export OMPI_MCA_btl=self,tcp; export OMP_NUM_THREADS=1
if ! command -v pw.x >/dev/null 2>&1 && [ -f "$HOME/miniconda3/bin/activate" ]; then
    source "$HOME/miniconda3/bin/activate"; fi

for MAT in graphene Al Si; do
  echo "=================== [$MAT] vc-relax ==================="
  mkdir -p ../tmp_${MAT}
  $QE_MPIRUN pw.x < ${MAT}.vc.in > ${MAT}.vc.out
  # vc.out의 최종 구조를 re.in에 반영
  python3 update_re.py ${MAT}.vc.out ${MAT}.re.in
  echo "------------------- [$MAT] relax -------------------"
  $QE_MPIRUN pw.x < ${MAT}.re.in > ${MAT}.re.out
  echo "[$MAT] 완료"
done
echo; echo "전체 완료. 비교: python3 plot_compare.py"
