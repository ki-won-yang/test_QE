#!/bin/bash
#SBATCH --job-name=qe_relax
#SBATCH --output=qe_relax.%j.out
#SBATCH --error=qe_relax.%j.err
#SBATCH --ntasks=8

# 제출 위치 = 단계 폴더 (예: .../QE/1_relax)
STAGEDIR=${SLURM_SUBMIT_DIR:-$PWD}
QEROOT="$(cd "$STAGEDIR/.." && pwd)"   # QE/ 최상위 절대경로
STAGE="$(basename "$STAGEDIR")"

# QE/ 전체를 컨테이너의 /work로 바인드.
# 단계 폴더(/work/$STAGE)에서 실행하므로 in파일의 ../pseudo, ../tmp_X 상대경로가
# 마스터와 완전히 동일하게 작동함 (경로 수정 불필요).
singularity exec \
  -B "$QEROOT:/work" \
  /singularity/quantum-mobile___1.0.0 \
  bash -lc "
    unset OPAL_PREFIX
    export OMPI_MCA_pml=ob1
    export OMPI_MCA_btl=self,tcp,vader
    export OMPI_MCA_oob=^ud
    export OMPI_MCA_btl_vader_single_copy_mechanism=none
    cd /work/$STAGE
    export QE_MPIRUN='mpirun -np ${SLURM_NTASKS}'
    bash run_all.sh
  "
