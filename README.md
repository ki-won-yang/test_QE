# Quantum ESPRESSO 실습 가이드

이 문서는 EDISON 실습 폴더에서 Quantum ESPRESSO(QE)를 이용해 구조 최적화, SCF, band structure, DOS/PDOS, Hubbard U 테스트를 실행하는 과정을 정리한 가이드입니다.

---

## 프로젝트 구조

```text
EDISON/
├── Tutorial.md
├── 0_setup/
│   ├── install_qe7.4.sh
│   ├── requirements.txt
│   └── setup_pseudo.sh
├── 1_relax/
│   ├── vc.in
│   ├── re.in
│   ├── run_op.sh
│   ├── plot_qe_energy_force.py
│   └── plot_qe_stress.py
├── 2_scf/
│   ├── scf.in
│   ├── run_scf.sh
│   └── plot_scf.py
├── 3_band/
│   ├── bands.in
│   ├── bands_pp.in
│   ├── run_bands.sh
│   └── plot_bands.py
├── 4_dos/
│   ├── nscf_dos.in
│   ├── dos.in
│   ├── pdos.in
│   ├── run_dos.sh
│   └── plot_dos.py
├── scf_U/
│   ├── scf.in
│   └── run_scf.sh
└── band_U/
    ├── bands.in
    ├── bands_pp.in
    ├── run_bands.sh
    └── plot_bands_U_compare.py
```

---

## 0. 사전 준비

실습 자료(GitHub 저장소) 다운로드

```bash
git clone https://github.com/ki-won-yang/test_QE.git
```

다운로드한 실습 폴더로 이동

```bash
cd test_QE
```

프로젝트 루트에서 필요한 pseudopotential을 준비합니다.

```bash
bash 0_setup/setup_pseudo.sh
```

---

## 1. QE 설치

실습용 웹 서버 환경에서는 Conda로 Quantum ESPRESSO를 설치합니다.

```bash
bash 0_setup/install_qe7.4.sh
```

설치 후 확인:

```bash
which pw.x
which bands.x
which dos.x
```

`pw.x`가 잡히지 않으면 현재 터미널에서 conda 환경을 활성화합니다.

```bash
source ~/miniconda3/bin/activate
which pw.x
```

Python 패키지를 설치합니다.

```bash
pip install -r 0_setup/requirements.txt
```
---

## 2. [실습 1] 구조 최적화: `vc-relax` 후 `relax`

### 2.1 개요

구조 최적화는 원자 위치와 격자 구조를 에너지가 낮아지는 방향으로 조정하는 계산입니다. 여기서는 먼저 `vc-relax`로 unit cell과 원자 위치를 함께 최적화한 뒤, 최종 구조를 `re.in`에 반영하여 `relax` 계산을 한 번 더 수행합니다.

- `vc-relax`: 원자 위치와 unit cell을 함께 최적화
- `relax`: unit cell은 고정하고 원자 위치만 최적화
- `vc.out`의 final coordinates를 `re.in`에 자동 반영

### 2.2 입력 파일 (`vc.in`, `re.in`)

`vc.in`은 cell까지 움직이는 계산이므로 다음처럼 설정합니다.

```fortran
&control
    calculation = 'vc-relax'
/
```

`re.in`은 `vc-relax` 이후 얻은 최종 cell을 기준으로 원자 위치만 다시 안정화하는 계산입니다.

```fortran
&control
    calculation = 'relax'
/
```

두 입력 파일에서 공통으로 중요한 항목은 다음과 같습니다.

- `prefix`: 계산 결과가 저장될 이름
- `pseudo_dir`: pseudopotential 파일 위치
- `outdir`: wavefunction과 charge density 저장 위치
- `ecutwfc`: plane-wave cutoff energy
- `K_POINTS`: Brillouin zone sampling
- `CELL_PARAMETERS`: unit cell vector
- `ATOMIC_POSITIONS`: 원자 좌표

### 2.3 실행

```bash
cd 1_relax
bash run_op.sh
```

실행 흐름:

```text
vc.in -> vc.out
vc.out final coordinates -> re.in 자동 업데이트
re.in -> re.out
```

수렴 확인 plot:

```bash
python3 plot_qe_energy_force.py re.out
python3 plot_qe_stress.py vc.out
```

생성되는 주요 그림:

```text
re.energy_force.png
vc.stress.png
```

---

## 3. [실습 2] SCF 계산

### 3.1 개요

SCF(Self-Consistent Field) 계산은 전자 밀도를 반복적으로 업데이트하여 self-consistent한 바닥 상태 전자 구조를 구하는 과정입니다.

### 3.2 실행

```bash
cd ../2_scf
bash run_scf.sh
python3 plot_scf.py
```

주요 결과:

```text
scf.out
scf_convergence.png
../tmp/
```

`scf.out`에서 다음 문구가 있으면 SCF가 정상 수렴한 것입니다.

```text
convergence has been achieved
```

---

## 4. [실습 3] Band Structure 계산

### 4.1 개요

Band structure 계산은 SCF에서 얻은 charge density를 이용해 고대칭 k-path를 따라 고유값을 계산하는 과정입니다.

계산 흐름:

```text
SCF 완료 -> pw.x calculation='bands' -> bands.x 후처리 -> Python plot
```

### 4.2 실행

SCF 계산이 먼저 끝나 있어야 합니다.

```bash
cd ../3_band
bash run_bands.sh
python3 plot_bands.py
```

주요 결과:

```text
bands.out
bands_pp.out
*.dat.gnu
band_structure.png
```

---

## 5. [실습 4] DOS / PDOS 계산

### 5.1 개요

DOS(Density of States)는 에너지별 전자 상태 수를 나타내고, PDOS(Projected DOS)는 원자 또는 orbital별 기여도를 분해해서 보여줍니다.

계산 흐름:

```text
SCF 완료 -> nscf 계산 -> dos.x / projwfc.x -> Python plot
```

### 5.2 실행

```bash
cd ../4_dos
bash run_dos.sh
python3 plot_dos.py
```

---

## 6. Hubbard U 테스트

`scf_U`와 `band_U` 폴더는 Hubbard U 값을 바꿔가며 SCF와 band structure를 비교하기 위한 예제입니다. 현재 설정은 MoS2 기준이며, Mo의 `4d` orbital에 U를 적용합니다.

### 6.1 SCF U별 계산

```bash
cd ../scf_U
bash run_scf.sh
```

이 스크립트는 U 값을 바꿔가며 SCF를 네 번 실행합니다.

```text
U = 0.0 eV -> ../tmp2/ -> scf_U0.0.out
U = 1.5 eV -> ../tmp3/ -> scf_U1.5.out
U = 3.0 eV -> ../tmp4/ -> scf_U3.0.out
U = 4.5 eV -> ../tmp5/ -> scf_U4.5.out
```

각 tmp 폴더 안에 wavefunction과 charge density가 저장됩니다.

```text
../tmp2/MoS2.save/
../tmp3/MoS2.save/
../tmp4/MoS2.save/
../tmp5/MoS2.save/
```

### 6.2 Band 계산

SCF가 끝난 뒤 상위 폴더로 돌아가서 `band_U` 폴더로 이동합니다.

```bash
cd ../band_U
bash run_bands.sh
```

이 스크립트는 각 U에 대응하는 tmp 폴더를 읽어서 band 계산과 `bands.x` 후처리를 실행합니다.

```text
U = 0.0 eV -> ../tmp2/ -> MoS2_bands_U0.0.dat.gnu
U = 1.5 eV -> ../tmp3/ -> MoS2_bands_U1.5.dat.gnu
U = 3.0 eV -> ../tmp4/ -> MoS2_bands_U3.0.dat.gnu
U = 4.5 eV -> ../tmp5/ -> MoS2_bands_U4.5.dat.gnu
```

### 6.3 Band 비교 plot

같은 `band_U` 폴더에서 실행합니다.

```bash
python3 plot_bands_U_compare.py
```

결과 그림:

```text
MoS2_bands_U_compare.png
```

이 plot은 각 U별 SCF output에서 Fermi energy를 읽어서, 각각의 band energy를 아래처럼 정렬합니다.

```text
E_band(U) - E_F(U)
```

기본 plot 범위는 Fermi level 기준 `-2 ~ 2 eV`입니다. 범위를 바꾸고 싶으면 다음처럼 실행합니다.

```bash
python3 plot_bands_U_compare.py --emin -1 --emax 1
```

전체 U 테스트 루틴:

```bash
cd scf_U
bash run_scf.sh

cd ../band_U
bash run_bands.sh
python3 plot_bands_U_compare.py
```

---

## 전체 실행 순서 요약

```bash
# 0. 환경 준비
pip install -r 0_setup/requirements.txt
bash 0_setup/setup_pseudo.sh

# 1. 구조 최적화
cd 1_relax
bash run_op.sh
python3 plot_qe_energy_force.py re.out
python3 plot_qe_stress.py vc.out
cd ..

# 2. SCF
cd 2_scf
bash run_scf.sh
python3 plot_scf.py
cd ..

# 3. Band
cd 3_band
bash run_bands.sh
python3 plot_bands.py
cd ..

# 4. DOS / PDOS
cd 4_dos
bash run_dos.sh
python3 plot_dos.py
cd ..

# 5. Hubbard U 테스트
cd scf_U
bash run_scf.sh
cd ../band_U
bash run_bands.sh
python3 plot_bands_U_compare.py
cd ..
```

---

## 자주 발생하는 오류

### `pw.x: command not found`

QE가 설치되지 않았거나 conda 환경이 활성화되지 않은 경우입니다.

```bash
source ~/miniconda3/bin/activate
which pw.x
```

그래도 잡히지 않으면 QE 설치를 다시 확인합니다.

```bash
bash 0_setup/install_qe7.4.sh
```

### `data-file-schema.xml not found`

SCF 계산 결과가 없는 상태에서 band, DOS, U-band 계산을 실행한 경우입니다. 먼저 대응되는 SCF 계산을 실행해야 합니다.

### `two consecutive same k`

`bands.x` 후처리에서 같은 k-point가 연속으로 들어간 경우입니다. `K_POINTS crystal_b` 경로에서 중복된 연속 k-point를 제거해야 합니다.

### `Unknown case for lda_plus_u_kind`

`U = 0.0`인데 `HUBBARD` 카드를 넣은 경우 발생할 수 있습니다. U가 0인 경우에는 `HUBBARD` 카드를 빼고 일반 DFT 계산으로 실행합니다.

