#!/bin/bash
#SBATCH --job-name=qe_band
#SBATCH --output=qe_band.%j.out
#SBATCH --error=qe_band.%j.err
#SBATCH --ntasks=8

# 제출 위치 = 단계 폴더 (예: .../QE/3_band)
STAGEDIR=${SLURM_SUBMIT_DIR:-$PWD}
QEROOT="$STAGEDIR/.."          # QE/ 최상위
STAGE=$(basename "$STAGEDIR")  # 예: 3_band

# QE/ 전체를 /work로 바인드 → tmp_X가 단계 간 공유됨 (band가 scf 결과 읽기 가능)
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

    for MAT in graphene Al Si; do
      echo \"=== [\${MAT}] bands ===\"
      mpirun -np \${SLURM_NTASKS} pw.x < \${MAT}.bands.in > \${MAT}.bands.out
      mpirun -np \${SLURM_NTASKS} bands.x < \${MAT}.bands_pp.in > \${MAT}.bands_pp.out
    done
  "
