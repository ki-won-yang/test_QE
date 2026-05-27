#!/bin/bash
# Run vc-relax, update re.in with the final vc-relax structure, then run relax.

set -euo pipefail

# Practice environment settings
export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp
export OMP_NUM_THREADS=1

if ! command -v pw.x >/dev/null 2>&1 && [ -f "$HOME/miniconda3/bin/activate" ]; then
    source "$HOME/miniconda3/bin/activate"
fi

QE_BIN=pw.x
VC_INPUT="vc.in"
VC_OUTPUT="vc.out"
RELAX_INPUT="re.in"
RELAX_OUTPUT="re.out"

mkdir -p ./tmp

echo "Job start: $(date)"
echo "QE_BIN: ${QE_BIN}"

echo "Running vc-relax: ${VC_INPUT} -> ${VC_OUTPUT}"
${QE_BIN} < "${VC_INPUT}" > "${VC_OUTPUT}"

TMP_COORD="$(mktemp)"
TMP_RELAX="$(mktemp)"
trap 'rm -f "${TMP_COORD}" "${TMP_RELAX}"' EXIT

awk '
  /Begin final coordinates/ {
    found = 1
    in_final = 1
    cell = ""
    atoms = ""
    mode = ""
    next
  }

  in_final && /End final coordinates/ {
    in_final = 0
    next
  }

  in_final && /^CELL_PARAMETERS/ {
    cell = $0 ORS
    mode = "cell"
    cell_lines = 0
    next
  }

  in_final && mode == "cell" {
    cell = cell $0 ORS
    cell_lines++
    if (cell_lines == 3) {
      mode = ""
    }
    next
  }

  in_final && /^ATOMIC_POSITIONS/ {
    atoms = $0 ORS
    mode = "atoms"
    next
  }

  in_final && mode == "atoms" {
    atoms = atoms $0 ORS
  }

  END {
    if (!found || cell == "" || atoms == "") {
      exit 1
    }
    printf "%s", cell
    printf "%s", atoms
  }
' "${VC_OUTPUT}" > "${TMP_COORD}"

awk '
  FNR == NR {
    if ($0 ~ /^CELL_PARAMETERS/) {
      coord_cell = $0 ORS
      mode = "cell"
      cell_lines = 0
      next
    }

    if (mode == "cell") {
      coord_cell = coord_cell $0 ORS
      cell_lines++
      if (cell_lines == 3) {
        mode = ""
      }
      next
    }

    if ($0 ~ /^ATOMIC_POSITIONS/) {
      coord_atoms = $0 ORS
      mode = "atoms"
      next
    }

    if (mode == "atoms") {
      coord_atoms = coord_atoms $0 ORS
      next
    }

    next
  }

  {
    if ($0 ~ /nat[[:space:]]*=/) {
      line = $0
      sub(/^.*nat[[:space:]]*=[[:space:]]*/, "", line)
      sub(/[^0-9].*$/, "", line)
      if (line != "") {
        nat = line + 0
      }
    }

    if (skip_cell > 0) {
      skip_cell--
      next
    }

    if (skip_atoms > 0) {
      skip_atoms--
      next
    }

    if (skip_until_card) {
      if ($0 ~ /^(K_POINTS|CONSTRAINTS|ATOMIC_VELOCITIES|ATOMIC_FORCES|OCCUPATIONS)/) {
        skip_until_card = 0
        print
      }
      next
    }

    if ($0 ~ /^CELL_PARAMETERS/) {
      printf "%s", coord_cell
      skip_cell = 3
      next
    }

    if ($0 ~ /^ATOMIC_POSITIONS/) {
      printf "%s", coord_atoms
      if (nat > 0) {
        skip_atoms = nat
      } else {
        skip_until_card = 1
      }
      next
    }

    print
  }
' "${TMP_COORD}" "${RELAX_INPUT}" > "${TMP_RELAX}"

cp "${RELAX_INPUT}" "${RELAX_INPUT}.bak"
mv "${TMP_RELAX}" "${RELAX_INPUT}"

echo "Updated ${RELAX_INPUT} from final coordinates in ${VC_OUTPUT}"
echo "Original relax input backup: ${RELAX_INPUT}.bak"

echo "Running relax: ${RELAX_INPUT} -> ${RELAX_OUTPUT}"
${QE_BIN} < "${RELAX_INPUT}" > "${RELAX_OUTPUT}"

echo "Job end: $(date)"
