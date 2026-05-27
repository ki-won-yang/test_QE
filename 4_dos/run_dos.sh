#!/bin/bash
# [실습 3] DOS / PDOS 계산 실행
# ⚠️ 반드시 1_scf/run_scf.sh 를 먼저 실행하세요.

# --- 조교 세팅: 에러 방지용 환경 변수 ---
export OMPI_MCA_pml=ob1
export OMPI_MCA_btl=self,tcp
export OMP_NUM_THREADS=1
# ----------------------------------------

if [ ! -f "../tmp/graphene.save/data-file-schema.xml" ]; then
    echo "❌ 에러: SCF 결과를 찾을 수 없습니다."
    echo "   1_scf/ 폴더에서 run_scf.sh 를 먼저 실행하세요."
    exit 1
fi

echo "[1/3] NSCF 계산 실행 중 (dense k-grid: 18×18×1)..."
pw.x < nscf_dos.in > nscf_dos.out

echo "[2/3] DOS 계산 실행 중..."
dos.x < dos.in > dos_out.log

echo "[3/3] PDOS 계산 실행 중..."
projwfc.x < pdos.in > pdos_out.log

echo "완료. python3 plot_dos.py 로 시각화하세요."