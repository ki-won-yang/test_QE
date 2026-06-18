#!/bin/bash
# Run band-structure calculations for SCF results with U = 0, 1, 2, 3 eV.
#SBATCH --partition=ice
set -euo pipefail

# Practice environment settings
export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp
export OMP_NUM_THREADS=1

if { ! command -v pw.x >/dev/null 2>&1 || ! command -v bands.x >/dev/null 2>&1; } && [ -f "$HOME/miniconda3/bin/activate" ]; then
    source "$HOME/miniconda3/bin/activate"
fi

QE_BIN=pw.x
BANDS_BIN=bands.x
BASE_SCF_INPUT="../5_scf_U/scf.in"
PREFIX="MoS2"

U_VALUES=("0.0" "1.5" "3.0" "4.5")
OUTDIRS=("../tmp2/" "../tmp3/" "../tmp4/" "../tmp5/")

write_kpath() {
    cat <<'KPATH'
K_POINTS crystal_b
8
0.000000  0.000000  0.000000  10  ! Gamma
0.500000  0.000000  0.000000  10  ! M
0.333333  0.333333  0.000000  10  ! K
0.000000  0.000000  0.000000  10  ! Gamma
0.000000  0.000000  0.500000  10  ! A
0.500000  0.000000  0.500000  10  ! L
0.333333  0.333333  0.500000  10  ! H
0.000000  0.000000  0.500000   1  ! A
KPATH
}

for idx in "${!U_VALUES[@]}"; do
    U_VALUE="${U_VALUES[$idx]}"
    OUTDIR="${OUTDIRS[$idx]}"
    TAG="U${U_VALUE}"
    BAND_INPUT="bands_${TAG}.in"
    BAND_OUTPUT="bands_${TAG}.out"
    BANDS_PP_INPUT="bands_pp_${TAG}.in"
    BANDS_PP_OUTPUT="bands_pp_${TAG}.out"
    FILBAND="MoS2_bands_${TAG}.dat"
    GNU_FILE="${FILBAND}.gnu"

    if [ ! -f "${OUTDIR}/${PREFIX}.save/data-file-schema.xml" ]; then
        echo "Error: SCF result not found: ${OUTDIR}/${PREFIX}.save/data-file-schema.xml"
        echo "Run ../5_scf_U/run_scf.sh first."
        continue
    fi

    awk -v outdir="${OUTDIR}" '
        BEGIN {
            in_control = 0
            in_system = 0
            added_verbosity = 0
            added_nbnd = 0
            skip_rest = 0
        }

        skip_rest {
            next
        }

        /^[[:space:]]*&control/ {
            in_control = 1
            print
            next
        }

        /^[[:space:]]*&system/ {
            in_system = 1
            print
            next
        }

        in_control && /^[[:space:]]*\// {
            if (!added_verbosity) {
                print "    verbosity = '\''high'\''"
                added_verbosity = 1
            }
            in_control = 0
            print
            next
        }

        in_system && /^[[:space:]]*\// {
            if (!added_nbnd) {
                print "    nbnd = 32"
                added_nbnd = 1
            }
            in_system = 0
            print
            next
        }

        /^[[:space:]]*calculation[[:space:]]*=/ {
            print "    calculation = '\''bands'\''"
            next
        }

        /^[[:space:]]*outdir[[:space:]]*=/ {
            print "    outdir = '\''" outdir "'\''"
            next
        }

        /^K_POINTS/ {
            skip_rest = 1
            next
        }

        /^HUBBARD([[:space:]]|\()/ {
            skip_rest = 1
            next
        }

        { print }
    ' "${BASE_SCF_INPUT}" > "${BAND_INPUT}"

    write_kpath >> "${BAND_INPUT}"

    if [ "${U_VALUE}" != "0.0" ]; then
        {
            echo ""
            echo "HUBBARD (ortho-atomic)"
            echo "U Mo-4d ${U_VALUE}"
        } >> "${BAND_INPUT}"
    fi

    cat > "${BANDS_PP_INPUT}" <<EOF
&bands
    prefix = '${PREFIX}'
    outdir = '${OUTDIR}'
    filband = '${FILBAND}'
    lsym = .false.
/
EOF

    rm -f "${FILBAND}" "${GNU_FILE}" "${FILBAND}.rap"

    echo "[1/2] Running bands for U=${U_VALUE} eV -> ${OUTDIR}"
    ${QE_BIN} < "${BAND_INPUT}" > "${BAND_OUTPUT}"

    if ! grep -q "End of band structure calculation" "${BAND_OUTPUT}"; then
        echo "Error: pw.x bands did not finish normally for U=${U_VALUE} eV."
        tail -n 40 "${BAND_OUTPUT}"
        continue
    fi

    echo "[2/2] Running bands.x for U=${U_VALUE} eV"
    ${BANDS_BIN} < "${BANDS_PP_INPUT}" > "${BANDS_PP_OUTPUT}"

    if [ ! -s "${GNU_FILE}" ]; then
        echo "Error: ${GNU_FILE} is missing or empty."
        echo "Last lines of ${BANDS_PP_OUTPUT}:"
        tail -n 60 "${BANDS_PP_OUTPUT}"
        continue
    fi

    echo "Done: ${GNU_FILE}"
done

echo "All band calculations finished."
