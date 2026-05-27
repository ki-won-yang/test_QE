# Quantum ESPRESSO 실습 가이드: Graphene 전자구조 계산

## 🎯 학습 목표

- Quantum ESPRESSO(QE) 7.5를 Conda를 통해 설치하고 `pw.x`를 구동할 수 있다.
- Graphene에 대해 SCF, Band structure, DOS/PDOS 계산을 수행할 수 있다.
- 파이썬을 활용해 계산 결과를 시각화하고 물리적 의미를 해석할 수 있다.

---

## 📁 프로젝트 구조

```
qe_tutorial/
├── Tutorial.md              ← 지금 보고 있는 문서
├── pseudo/                  ← [공유] 슈도포텐셜 (전 실습 공통)
│   └── C_ONCV_PBE_sr.upf
├── tmp/                     ← [공유] 계산 결과 (SCF → Band, DOS 순으로 공유)
│
├── 0_setup/                 ← 환경 준비
│   ├── install_qe7.4.sh     ← Miniconda 및 QE 우회 설치 스크립트
│   ├── setup_pseudo.sh
│   └── requirements.txt
│
├── 1_scf/                   ← 실습 1: SCF 계산
│   ├── scf.in
│   ├── run_scf.sh
│   └── plot_scf.py
│
├── 2_band/                  ← 실습 2: Band Structure
│   ├── bands.in
│   ├── bands_pp.in
│   ├── run_bands.sh
│   └── plot_bands.py
│
└── 3_dos/                   ← 실습 3: DOS / PDOS
    ├── nscf_dos.in
    ├── dos.in
    ├── pdos.in
    ├── run_dos.sh
    └── plot_dos.py
```

> ⚠️ **`pseudo/`와 `tmp/` 폴더는 프로젝트 루트에 위치하며 전 실습이 공유합니다.** 모든 입력 파일의 `pseudo_dir`과 `outdir`이 `'../pseudo/'`, `'../tmp/'`로 설정되어 있어, 각 실습 폴더에서 실행하면 자동으로 공유 경로를 참조합니다.

---

## 0. 실습 자료 다운로드 및 환경 준비

가장 먼저 실습에 필요한 모든 코드와 데이터를 GitHub에서 다운로드합니다.
터미널을 열고 아래 명령어를 순서대로 입력하세요.

```bash
# 1. 실습 자료(GitHub 저장소) 다운로드
git clone [https://github.com/ki-won-yang/test_QE.git](https://github.com/ki-won-yang/test_QE.git)

# 2. 다운로드한 실습 폴더로 이동 (매우 중요!)
cd test_QE

# 3. 파이썬 라이브러리 설치
pip install -r 0_setup/requirements.txt

# 4. 슈도포텐셜 다운로드 (pseudo/ 폴더에 저장됨)
bash 0_setup/setup_pseudo.sh
```

> ⚠️ **중요**: 슈도포텐셜 파일에 `PP_PSWFC` 블록이 포함되어야 실습 3의 PDOS 계산이 가능합니다. `setup_pseudo.sh`가 자동으로 검증합니다.

---

## 1. QE 설치 (Conda 방식)

실습용 웹 서버 환경에 맞추어 Conda를 통해 Quantum ESPRESSO를 빠르고 안정적으로 설치합니다. (약 2~3분 소요) 복잡한 컴파일 과정이 생략됩니다.

```bash
bash 0_setup/install_qe7.4.sh
```

> ⚠️ **중요**: 설치가 완료되면 반드시 현재 터미널 창을 닫고, 메뉴에서 **Terminal > New Terminal**을 클릭해 '새 터미널'을 열어주세요. 새 터미널을 열면 어디서든 `pw.x`, `bands.x`, `dos.x`, `projwfc.x` 명령어를 바로 사용할 수 있습니다.

---

## 2. [실습 1] SCF 계산 — 바닥 상태 에너지 구하기

### 2.1 개요

SCF(Self-Consistent Field) 계산은 전자 밀도와 퍼텐셜을 반복적으로 업데이트하여 시스템의 바닥 상태 에너지를 자기 모순 없이(self-consistently) 구합니다.

### 2.2 입력 파일 (`1_scf/scf.in`)

핵심 파라미터:

- **`ecutwfc = 50.0`**: 파동함수의 평면파 차단 에너지 (Ry). 클수록 정확하지만 계산 비용이 증가합니다.
- **`K_POINTS {automatic} 9 9 1`**: 브릴루앙 존 샘플링. 2D 물질이므로 z 방향은 1입니다.
- **`occupations = 'smearing'`**: 금속/반금속 시스템에 적합한 점유 방식입니다.

### 2.3 실행

```bash
cd 1_scf
bash run_scf.sh
python3 plot_scf.py
```

`scf.out`에서 `convergence has been achieved in N iterations` 메시지를 확인하고, `scf_convergence.png`에서 수렴 그래프를 확인하세요.

---

## 3. [실습 2] Band Structure 계산 — 에너지 밴드 그리기

### 3.1 개요

Band structure는 전자의 에너지-운동량(E-k) 관계를 보여줍니다. Graphene의 K점에서 나타나는 **디랙 콘(Dirac cone)** — 선형으로 교차하는 밴드 — 은 제로갭 반금속의 핵심 시그니처입니다.

### 3.2 계산 흐름

SCF 전하 밀도를 고정한 채 고대칭 경로(Γ → M → K → Γ)를 따라 고유값만 구하는 non-self-consistent 계산입니다.

```
[1_scf 완료] → pw.x (calculation='bands') → bands.x (후처리) → Python (시각화)
```

### 3.3 입력 파일 (`2_band/bands.in`)

SCF와 달라지는 부분:

- **`calculation = 'bands'`**: 밴드 계산 모드
- **`nbnd = 12`**: 비점유 밴드까지 포함 (점유 밴드 4개 + 비점유)
- **`K_POINTS {crystal_b}`**: 고대칭 경로 (각 구간 30포인트)

### 3.4 실행

```bash
cd 2_band
bash run_bands.sh
python3 plot_bands.py
```

> ⚠️ **SCF가 먼저 완료되어야 합니다.** `../tmp/graphene.save/`가 없으면 에러가 발생합니다.

> 💡 **확인 포인트**: K점에서 밴드가 페르미 에너지 근처에서 **선형으로 교차**(디랙 콘)하는지 확인하세요.

---

## 4. [실습 3] DOS / PDOS 계산 — 상태 밀도 분석

### 4.1 개요

DOS(Density of States)는 에너지별 전자 상태의 밀도, PDOS(Projected DOS)는 이를 궤도별(s, p)로 분해한 것입니다.

### 4.2 계산 흐름

```
[1_scf 완료] → pw.x (nscf, 18×18×1) → dos.x (Total DOS)     → Python
                                      → projwfc.x (PDOS)      → Python
```

### 4.3 입력 파일 (`3_dos/`)

SCF와 달라지는 핵심:

- **`calculation = 'nscf'`**: 전하 밀도 고정, 고유값만 재계산
- **`occupations = 'tetrahedra'`**: DOS에 적합한 tetrahedron 방법 (SCF의 `smearing`과 다름)
- **`K_POINTS 18 18 1`**: 2배 촘촘한 격자로 부드러운 DOS 확보

### 4.4 실행

```bash
cd 3_dos
bash run_dos.sh
python3 plot_dos.py
```

> 💡 **확인 포인트**:
> - **Total DOS**: 페르미 에너지 근처 V자 형태 (vanishing DOS) → 디랙 콘의 특징
> - **PDOS**: E_F 근처는 **C-p**(π 결합), 심층(−20 eV)은 **C-s**가 지배

---

## 실행 순서 전체 요약

```bash
# 0. 환경 준비 (프로젝트 루트에서)
pip install -r 0_setup/requirements.txt
bash 0_setup/setup_pseudo.sh

# 1. SCF
cd 1_scf && bash run_scf.sh && python3 plot_scf.py && cd ..

# 2. Band Structure
cd 2_band && bash run_bands.sh && python3 plot_bands.py && cd ..

# 3. DOS / PDOS
cd 3_dos && bash run_dos.sh && python3 plot_dos.py && cd ..
```

---

## ❓ 트러블슈팅

**Q. `xml data file ./tmp/graphene.save/data-file-schema.xml not found`**
→ SCF를 먼저 실행하지 않았거나, 프로젝트 루트 밖에서 실행한 경우. 반드시 각 실습 폴더(`1_scf/`, `2_band/`, `3_dos/`) 안에서 스크립트를 실행하세요. `../tmp/`에 SCF 결과가 있어야 합니다.

**Q. `pw.x: command not found`**
→ QE 설치 후 새 터미널을 열지 않아서 Conda 환경(`(base)`)이 활성화되지 않은 경우입니다. 터미널 창을 닫고 다시 열어주세요.
→ 또는 실행 스크립트(`run_xxx.sh`) 내부에 `/pw.x` 처럼 앞에 슬래시가 붙어있다면 슬래시를 지워주세요.

**Q. `Cannot project on zero atomic wavefunctions!` (projwfc.x)**
→ 슈도포텐셜에 `PP_PSWFC` 블록이 없을 때 발생합니다. `grep "PP_PSWFC" pseudo/C_ONCV_PBE_sr.upf`로 확인하세요. 없다면 `bash 0_setup/setup_pseudo.sh`로 재다운로드 후 SCF부터 다시 돌려야 합니다.

**Q. 계산이 멈춘 것처럼 너무 오래 걸립니다.**
→ 웹 서버의 MPI 통신 충돌입니다. 실습 스크립트 내부에 `export OMP_NUM_THREADS=1` 등의 설정이 정상적으로 들어있는지 확인하세요.

**Q. Band 그래프가 smooth하지 않다**
→ `bands.in`의 K_POINTS 구간 포인트 수(기본 30)를 50~60으로 늘려보세요.

**Q. DOS 그래프가 들쭉날쭉하다**
→ `nscf_dos.in`의 k-grid를 `24 24 1` 또는 `36 36 1`로 늘리면 부드러워집니다.
