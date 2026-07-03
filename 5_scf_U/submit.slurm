#!/bin/bash
#SBATCH --job-name=qe_scfU
#SBATCH --output=qe_scfU.%j.out
#SBATCH --error=qe_scfU.%j.err
#SBATCH --ntasks=8

# 제출 위치 = 단계 폴더 (예: .../QE/5_scf_U)
STAGEDIR=${SLURM_SUBMIT_DIR:-$PWD}
QEROOT="$(cd "$STAGEDIR/.." && pwd)"   # QE/ 최상위 절대경로
STAGE="$(basename "$STAGEDIR")"

# QE/ 전체를 컨테이너의 /work로 바인드.
# 단계 폴더(/work/$STAGE)에서 실행 → ../tmp2~5, ../pseudo 상대경로가
# 마스터와 동일하게 작동 (band_U는 scf_U가 만든 tmp2~5를 그대로 읽음).
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
    bash run_scf.sh
  "
