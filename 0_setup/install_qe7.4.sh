#!/bin/bash
set -euo pipefail
# ============================================================
# Quantum ESPRESSO 설치 스크립트 (Conda 우회 방식 - sudo 불필요)
# ============================================================

echo "================================================"
echo " 실습용 QE 설치를 시작합니다. (약 2~3분 소요)"
echo "================================================"

echo "[1/3] 사용자 환경용 Miniconda 설치 중..."
# 기존에 설치된 conda가 없다면 설치
if [ ! -d "$HOME/miniconda3" ]; then
    mkdir -p $HOME/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O $HOME/miniconda3/miniconda.sh
    bash $HOME/miniconda3/miniconda.sh -b -u -p $HOME/miniconda3
    rm $HOME/miniconda3/miniconda.sh
    $HOME/miniconda3/bin/conda init bash
fi

echo "[2/3] Conda 환경 활성화..."
source $HOME/miniconda3/bin/activate

if conda tos --help >/dev/null 2>&1; then
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main || true
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r || true
fi

echo "[3/3] Quantum ESPRESSO 다운로드 중 (컴파일 불필요)..."
# conda-forge에서 qe 패키지 설치
conda install --override-channels -c conda-forge qe -y

if ! command -v pw.x >/dev/null 2>&1; then
    echo "ERROR: pw.x not found after installation."
    exit 1
fi

echo ""
echo "================================================"
echo " ✅ 설치 완료!"
echo " 이제 터미널 창을 닫고 '새 터미널(New Terminal)'을 열어주세요."
echo " 새 터미널에서 'pw.x'를 입력하시면 바로 실행됩니다."
echo "================================================"
