#!/bin/bash
#SBATCH --job-name=qe_dos
#SBATCH --output=qe_dos.%j.out
#SBATCH --error=qe_dos.%j.err
#SBATCH --ntasks=8

# 제출 위치 = 단계 폴더 (예: .../QE/4_dos)
STAGEDIR=${SLURM_SUBMIT_DIR:-$PWD}
QEROOT="$STAGEDIR/.."          # QE/ 최상위
STAGE=$(basename "$STAGEDIR")  # 예: 4_dos

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
      echo \"=== [\${MAT}] nscf + dos ===\"
      mpirun -np \${SLURM_NTASKS} pw.x < \${MAT}.nscf.in > \${MAT}.nscf.out
      mpirun -np \${SLURM_NTASKS} dos.x < \${MAT}.dos.in > \${MAT}.dos.out
    done
  "
