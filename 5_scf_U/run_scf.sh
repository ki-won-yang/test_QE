#!/bin/bash
# Run SCF calculations for multiple Hubbard U values.
set -euo pipefail
# 마스터: 빈 값(직렬) / 노드 slurm: mpirun -np N 주입
QE_MPIRUN="${QE_MPIRUN:-}"

# Practice environment settings
export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp
export OMP_NUM_THREADS=1

if ! command -v pw.x >/dev/null 2>&1 && [ -f "$HOME/miniconda3/bin/activate" ]; then
    source "$HOME/miniconda3/bin/activate"
fi

QE_BIN=pw.x
BASE_INPUT="scf.in"

U_VALUES=("0.0" "1.5" "3.0" "4.5")
OUTDIRS=("../tmp2/" "../tmp3/" "../tmp4/" "../tmp5/")

for idx in "${!U_VALUES[@]}"; do
    U_VALUE="${U_VALUES[$idx]}"
    OUTDIR="${OUTDIRS[$idx]}"
    TAG="U${U_VALUE}"
    INPUT_FILE="scf_${TAG}.in"
    OUTPUT_FILE="scf_${TAG}.out"

    mkdir -p "${OUTDIR}"

    awk -v outdir="${OUTDIR}" '
        /^[[:space:]]*outdir[[:space:]]*=/ {
            print "    outdir = '\''" outdir "'\''"
            next
        }

        /^HUBBARD([[:space:]]|\()/ {
            skip_hubbard = 1
            next
        }

        skip_hubbard && /^[[:space:]]*(U|J0|J|V|ALPHA)[[:space:]]+/ {
            next
        }

        skip_hubbard {
            skip_hubbard = 0
        }

        { print }
    ' "${BASE_INPUT}" > "${INPUT_FILE}"

    if [ "${U_VALUE}" != "0.0" ]; then
        {
            echo ""
            echo "HUBBARD (ortho-atomic)"
            echo "U Mo-4d ${U_VALUE}"
        } >> "${INPUT_FILE}"
    fi

    echo "Running SCF for U=${U_VALUE} eV -> ${OUTDIR}"
    $QE_MPIRUN ${QE_BIN} < "${INPUT_FILE}" > "${OUTPUT_FILE}"
    echo "Done: ${OUTPUT_FILE}"
done

echo "All SCF calculations finished."
