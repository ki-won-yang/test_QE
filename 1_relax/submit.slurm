#!/bin/bash
#SBATCH --job-name=qe_relax
#SBATCH --output=qe_relax.%j.out
#SBATCH --error=qe_relax.%j.err
#SBATCH --ntasks=8

# 제출 위치 = 단계 폴더 (예: .../QE/1_relax)
STAGEDIR=${SLURM_SUBMIT_DIR:-$PWD}
QEROOT="$STAGEDIR/.."          # QE/ 최상위
STAGE=$(basename "$STAGEDIR")  # 예: 1_relax

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
      mkdir -p /work/tmp_\${MAT}
      echo \"=== [\${MAT}] vc-relax ===\"
      mpirun -np \${SLURM_NTASKS} pw.x < \${MAT}.vc.in > \${MAT}.vc.out
      echo \"=== [\${MAT}] relax ===\"
      mpirun -np \${SLURM_NTASKS} pw.x < \${MAT}.re.in > \${MAT}.re.out
    done
  "
