#!/bin/bash
# [실습 1] SCF 계산 실행

# --- 조교 세팅: 에러 방지용 환경 변수 ---
export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp
export OMP_NUM_THREADS=1
# ----------------------------------------

if ! command -v pw.x >/dev/null 2>&1 && [ -f "$HOME/miniconda3/bin/activate" ]; then
    source "$HOME/miniconda3/bin/activate"
fi

QE_BIN=pw.x

mkdir -p ../tmp

echo "SCF 계산 실행 중..."
$QE_BIN < scf.in > scf.out
