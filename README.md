# Quantum ESPRESSO 실습 가이드

이 문서는 EDISON 여름학교 실습에서 Quantum ESPRESSO(QE)로 **구조 최적화 → SCF → Band Structure → DOS → Hubbard U 비교**를 수행하는 과정을 정리한 가이드입니다.

- **실습 1~4 (Graphene · Al · Si 동시)**: 각 단계에서 **금속(Al) · 반도체(Si) · 반금속(Graphene)** 세 물질을 한 번에 돌려 전도성 차이를 직접 비교합니다.
- **실습 5 (MoS₂)**: Hubbard U 값에 따른 band 구조 변화를 비교합니다.

### 핵심 설계: 물질 × 단계 매트릭스

각 단계 폴더(`1_relax`~`4_dos`)에서 `run_all.sh` 한 번이면 **세 물질이 연속으로** 계산되고, `plot_compare.py`가 결과를 나란히 비교합니다. "지금은 SCF 단계인데 금속·반도체·반금속이 이렇게 다르다"를 같은 화면에서 보여주는 구조입니다.

| 물질 | 구조 | 분류 | 핵심 특징 | smearing |
|------|------|------|-----------|----------|
| **Al** | FCC | 금속 | E<sub>F</sub>에서 DOS>0, band가 E<sub>F</sub> 교차 | `mp` |
| **Si** | diamond | 반도체 | E<sub>F</sub> 주변 band gap (~0.6 eV, PBE) | `fixed` |
| **Graphene** | hexagonal | 반금속 | E<sub>F</sub>에서 DOS=0 (디랙 콘) | `gaussian` |

> **파일 규칙**: 각 단계 폴더에 `{물질}.{단계}.in` 형태로 입력이 있습니다 (예: `Al.scf.in`, `Si.bands.in`). `outdir`은 물질별로 `../tmp_graphene/`, `../tmp_Al/`, `../tmp_Si/`로 분리되어 단계 간(SCF→band/dos) 공유됩니다.

---

## 프로젝트 구조

```text
QE/
├── README.md                ← 지금 보고 있는 문서
├── pseudo/                  ← [공유] pseudopotential (전 실습 공통)
│   ├── C_ONCV_PBE_sr.upf    (Graphene용)
│   ├── Al_ONCV_PBE_sr.upf   (Al용)
│   ├── Si_ONCV_PBE_sr.upf   (Si용)
│   ├── Mo.pbe-n-nc.UPF      (MoS₂용)
│   └── S.pbe-n-nc.UPF       (MoS₂용)
│
├── 0_setup/                 ← 환경 준비
│   ├── install_qe7.4.sh
│   ├── setup_pseudo.sh
│   └── requirements.txt
│
├── 1_relax/                 ← [실습 1] 구조 최적화 (vc-relax → relax)
│   ├── {graphene,Al,Si}.vc.in / {graphene,Al,Si}.re.in
│   ├── run_all.sh           ← 세 물질 일괄 실행
│   ├── update_re.py         ← vc-relax 최종 구조를 re.in에 반영
│   ├── plot_compare.py      ← relax_compare.png
│   ├── plot_qe_energy_force.py
│   └── plot_qe_stress.py
│
├── 2_scf/                   ← [실습 2] SCF
│   ├── {graphene,Al,Si}.scf.in
│   ├── run_all.sh
│   └── plot_compare.py      ← scf_compare.png
│
├── 3_band/                  ← [실습 3] Band Structure
│   ├── {graphene,Al,Si}.bands.in / {graphene,Al,Si}.bands_pp.in
│   ├── run_all.sh
│   └── plot_compare.py      ← bands_compare.png
│
├── 4_dos/                   ← [실습 4] DOS
│   ├── {graphene,Al,Si}.nscf.in / {graphene,Al,Si}.dos.in
│   ├── run_all.sh
│   └── plot_compare.py      ← dos_compare.png
│
├── 5_scf_U/                 ← [실습 5-1] Hubbard U SCF (U값별)
│   ├── scf.in
│   └── run_scf.sh
│
└── 5_band_U/                ← [실습 5-2] Hubbard U Band 비교
    ├── bands.in / bands_pp.in
    ├── run_bands.sh
    └── plot_bands_U_compare.py
```

> **`pseudo/` 폴더는 프로젝트 루트에서 공유됩니다.** 모든 입력 파일의 `pseudo_dir`이 `'../pseudo/'`로 설정되어 있어, 각 단계 폴더에서 실행하면 자동으로 공유 pseudopotential을 참조합니다. `outdir`은 물질별(`../tmp_graphene/`, `../tmp_Al/`, `../tmp_Si/`)로 분리되어 단계 간에 공유되므로, band/DOS가 SCF의 charge density를 읽을 수 있습니다.

---

## 0. 사전 준비

### 0.1 실습 자료 다운로드

```bash
git clone https://github.com/YHKlab/ESEC2026.git
cd ESEC2026/QE
```

### 0.2 QE 설치 (Conda 방식)

실습용 웹 서버 환경에서는 Conda로 Quantum ESPRESSO를 설치합니다. (약 2~3분 소요)

```bash
bash 0_setup/install_qe7.4.sh
```

> **중요**: 설치 완료 후 반드시 터미널 창을 닫고 **새 터미널(New Terminal)**을 열어주세요. 그래야 `pw.x`, `bands.x`, `dos.x`, `projwfc.x` 명령어가 활성화됩니다.

설치 확인:

```bash
which pw.x
```

잡히지 않으면 conda 환경을 직접 활성화합니다.

```bash
source ~/miniconda3/bin/activate
which pw.x
```

### 0.3 pseudopotential 및 Python 패키지 준비

```bash
# pseudopotential 확인 (pseudo/ 폴더에 이미 포함됨)
bash 0_setup/setup_pseudo.sh

# Python 패키지 설치
pip install -r 0_setup/requirements.txt
```

---

## 1. [실습 1] 구조 최적화 (`vc-relax` → `relax`)

### 1.1 개요

구조 최적화는 원자 위치와 격자를 에너지가 낮아지는 방향으로 조정하는 계산입니다. 먼저 `vc-relax`로 unit cell과 원자 위치를 함께 최적화한 뒤, 최종 구조를 기준으로 `relax`를 한 번 더 수행합니다.

- **`vc-relax`** (`{물질}.vc.in`): 원자 위치 + unit cell 동시 최적화
- **`relax`** (`{물질}.re.in`): unit cell 고정, 원자 위치만 최적화
- `*.vc.out`의 final coordinates가 `*.re.in`에 자동 반영됩니다 (`update_re.py`).

> Graphene은 2D라 진공 방향을 고정하기 위해 `cell_dofree='xy'`, `nosym=.true.`를 사용하고, Al·Si는 3D라 전체 셀 최적화(`cell_dofree='all'`)를 사용합니다.

### 1.2 실행

```bash
cd 1_relax
bash run_all.sh          # graphene, Al, Si 순서로 vc-relax→relax
python3 plot_compare.py  # → relax_compare.png (세 물질 수렴 비교)
```

물질별 실행 흐름:

```text
*.vc.in → *.vc.out → (final coordinates 추출) → *.re.in 자동 업데이트 → *.re.out
```

단일 물질 수렴 확인(선택):

```bash
python3 plot_qe_energy_force.py graphene.re.out   # → 에너지/force 수렴
python3 plot_qe_stress.py graphene.vc.out         # → stress 수렴
```

### 1.3 결과 해석

- **`relax_compare.png`**: 세 물질의 최적화 step에 따른 total energy입니다. Force가 0에 가까워지면 원자가 안정한 위치에 도달한 것입니다. Al·Si는 실험 격자상수가 잘 알려져 있어 거의 변하지 않는데, "최적화하니 실험값과 일치하더라"가 오히려 좋은 검증 메시지가 됩니다.

---

## 2. [실습 2] SCF 계산

### 2.1 개요

SCF(Self-Consistent Field) 계산은 전자 밀도를 반복적으로 업데이트하여 self-consistent한 바닥 상태 전자 구조를 구하는 과정입니다.

### 2.2 실행

```bash
cd ../2_scf
bash run_all.sh          # 세 물질 SCF
python3 plot_compare.py  # → scf_compare.png
```

`*.scf.out`에서 `convergence has been achieved` 문구가 있으면 정상 수렴입니다.

### 2.3 결과 해석

- **`scf_compare.png`**: SCF iteration에 따라 total energy가 수렴하는 과정입니다. 에너지가 점차 감소하다가 평평해지면(수렴) 바닥 상태를 정확히 찾은 것입니다. 이 SCF 결과(charge density)가 이후 Band, DOS 계산의 기반이 됩니다.

---

## 3. [실습 3] Band Structure 계산

### 3.1 개요

SCF에서 얻은 charge density를 고정한 채, 고대칭 k-path를 따라 고유값을 계산합니다. 결정 구조가 다르면 Brillouin zone도 다르므로 k-path는 물질마다 다릅니다.

```text
SCF 완료 → pw.x (calculation='bands') → bands.x 후처리 → Python plot
```

### 3.2 실행

> SCF(실습 2)가 먼저 완료되어 있어야 합니다.

```bash
cd ../3_band
bash run_all.sh          # 세 물질 band (각자 k-path)
python3 plot_compare.py  # → bands_compare.png
```

> k-path가 물질마다 다릅니다: Graphene은 hexagonal(Γ-M-K-Γ), Al·Si는 FCC(Γ-X-W-K-Γ-L). 구조가 다르면 Brillouin zone도 달라진다는 것 자체가 학습 포인트입니다.

### 3.3 결과 해석

- **`bands_compare.png`**: 세 물질의 E-k를 나란히 비교합니다. **Al은 여러 band가 E<sub>F</sub>를 가로질러**(금속), **Si는 E<sub>F</sub> 주변에 명확한 gap**(반도체), **Graphene은 K점에서 디랙 콘으로 한 점에서만 닿음**(반금속). 전도성의 차이가 band 구조에서 가장 극적으로 드러나는 그림입니다.

---

## 4. [실습 4] DOS 계산

### 4.1 개요

DOS(Density of States)는 에너지별 전자 상태 수입니다. 조밀한 NSCF k-grid 계산 후 `dos.x`로 구합니다.

```text
SCF 완료 → nscf 계산 → dos.x → Python plot
```

### 4.2 실행

```bash
cd ../4_dos
bash run_all.sh          # 세 물질 nscf + dos
python3 plot_compare.py  # → dos_compare.png (전도성 비교의 핵심)
```

### 4.3 결과 해석

- **`dos_compare.png`**: 위→아래로 Graphene·Al·Si의 DOS를 쌓아 보여줍니다. **E<sub>F</sub>(점선)에서의 DOS 값이 전도성을 가르는 결정적 지표**입니다 — Al은 유한(금속), Si는 0인 갭(반도체), Graphene은 V자로 한 점에서 0에 닿음(반금속). PBE는 Si gap을 ~0.6 eV로 과소평가하는데(실험 1.1 eV), 이는 실습 5의 Hubbard U가 왜 필요한지로 자연스럽게 연결됩니다.

---

## 5. [실습 5] Hubbard U 테스트 (MoS₂)

### 5.1 개요

일반 DFT는 d/f orbital을 가진 물질의 band gap을 과소평가하는 경향이 있습니다. **Hubbard U** 보정은 localized orbital에 on-site 반발항을 추가하여 이를 개선합니다. 여기서는 MoS₂의 **Mo-4d orbital**에 U값(0.0, 1.5, 3.0, 4.5 eV)을 바꿔가며 band 구조 변화를 비교합니다.

### 5.2 SCF 계산 (U값별)

```bash
cd ../5_scf_U
bash run_scf.sh
```

이 스크립트는 `scf.in`을 기반으로 U값을 바꿔가며 SCF를 4회 실행합니다. (`HUBBARD` 카드를 자동으로 추가/제거)

```text
U = 0.0 eV → ../tmp2/ → scf_U0.0.out   (U=0: HUBBARD 카드 없이 일반 DFT)
U = 1.5 eV → ../tmp3/ → scf_U1.5.out
U = 3.0 eV → ../tmp4/ → scf_U3.0.out
U = 4.5 eV → ../tmp5/ → scf_U4.5.out
```

### 5.3 Band 계산 및 비교

```bash
cd ../5_band_U
bash run_bands.sh
python3 plot_bands_U_compare.py
```

각 U값에 대응하는 `tmp` 폴더를 읽어 band 계산을 수행하고, 결과를 하나의 그래프에 겹쳐 그립니다. 각 band는 해당 U의 Fermi energy 기준으로 정렬됩니다. (`E_band(U) − E_F(U)`)

> 기본 plot 범위는 Fermi level 기준 −2 ~ 2 eV입니다. 범위 조정:
> ```bash
> python3 plot_bands_U_compare.py --emin -1 --emax 1
> ```

### 5.4 결과 해석

- **`MoS2_bands_U_compare.png`**: U값이 커질수록 band 구조가 어떻게 변하는지를 한 그래프에서 비교합니다. 일반적으로 **U가 증가하면 band gap이 넓어지는** 경향을 확인할 수 있으며, 이는 Hubbard 보정이 d-orbital의 과소평가된 gap을 교정하기 때문입니다. 실험값과 비교하여 적절한 U값을 선택하는 것이 DFT+U 계산의 핵심입니다.

---

## 전체 실행 순서 요약

```bash
# 0. 환경 준비
bash 0_setup/install_qe7.4.sh     # (설치 후 새 터미널)
bash 0_setup/setup_pseudo.sh
pip install -r 0_setup/requirements.txt

# 1. 구조 최적화 (세 물질)
cd 1_relax && bash run_all.sh && python3 plot_compare.py && cd ..

# 2. SCF (세 물질)
cd 2_scf && bash run_all.sh && python3 plot_compare.py && cd ..

# 3. Band (세 물질, 각자 k-path)
cd 3_band && bash run_all.sh && python3 plot_compare.py && cd ..

# 4. DOS (세 물질 — 전도성 비교 핵심)
cd 4_dos && bash run_all.sh && python3 plot_compare.py && cd ..

# 5. Hubbard U 테스트 (MoS₂)
cd 5_scf_U && bash run_scf.sh && cd ..
cd 5_band_U && bash run_bands.sh && python3 plot_bands_U_compare.py && cd ..
```

---

## 자주 발생하는 오류

**`pw.x: command not found`**
→ QE 설치 후 새 터미널을 열지 않아 conda 환경이 활성화되지 않은 경우입니다.
```bash
source ~/miniconda3/bin/activate
which pw.x
```

**`data-file-schema.xml not found`**
→ SCF 결과 없이 band/DOS/U-band 계산을 실행한 경우입니다. 대응되는 SCF를 먼저 실행하세요. (실습 5는 `5_scf_U`를 먼저 실행)

**`two consecutive same k`**
→ `bands.x` 후처리에서 같은 k-point가 연속으로 들어간 경우입니다. `K_POINTS crystal_b` 경로에서 중복된 연속 k-point를 제거하세요.

**`Unknown case for lda_plus_u_kind`**
→ `U = 0.0`인데 `HUBBARD` 카드를 넣은 경우입니다. U=0이면 `HUBBARD` 카드를 빼고 일반 DFT로 실행해야 합니다. (`5_scf_U/run_scf.sh`는 이미 자동 처리)

**`Cannot project on zero atomic wavefunctions!` (projwfc.x)**
→ pseudopotential에 `PP_PSWFC` 블록이 없을 때 발생합니다. `pseudo/` 폴더의 UPF 파일을 확인하세요.
