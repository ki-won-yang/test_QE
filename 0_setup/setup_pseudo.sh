#!/bin/bash
# 슈도포텐셜 다운로드 및 검증
# 프로젝트 루트의 pseudo/ 폴더에 저장합니다.

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PSEUDO_DIR="$SCRIPT_DIR/../pseudo"
mkdir -p "$PSEUDO_DIR"

echo "Carbon 슈도포텐셜 다운로드 중..."
wget -O "$PSEUDO_DIR/C_ONCV_PBE_sr.upf" \
    https://raw.githubusercontent.com/pipidog/ONCVPSP/master/abinit/C_ONCV_PBE_sr.upf

if grep -q "PP_PSWFC" "$PSEUDO_DIR/C_ONCV_PBE_sr.upf" 2>/dev/null; then
    echo "✅ 다운로드 및 검증 완료 (PP_PSWFC 포함 확인)"
    echo "   저장 위치: $PSEUDO_DIR/C_ONCV_PBE_sr.upf"
else
    echo "⚠️  다운로드 실패 또는 PP_PSWFC 블록이 없습니다."
    echo "   수동 다운로드: https://github.com/pipidog/ONCVPSP/tree/master/abinit"
fi
