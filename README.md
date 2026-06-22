# Quantum ESPRESSO Practical Guide



This document is a guide summarizing the process of performing **structural optimization $\rightarrow$ SCF $\rightarrow$ Band Structure $\rightarrow$ DOS/PDOS $\rightarrow$ Hubbard U comparison** using Quantum ESPRESSO (QE) in the EDISON summer school practical session.

* **Practices 1~4 (Graphene)**: Learning the basic workflow of QE.


* **Practice 5 (MoS₂)**: Comparing the changes in band structure according to Hubbard U values.



---

## Project Structure



```text
QE/
├── README.md                ← The document you are currently reading[cite: 1]
├── pseudo/                  ← [Shared] pseudopotential (Common for all practices)
│   ├── C_ONCV_PBE_sr.upf    (For Graphene)
│   ├── Mo.pbe-n-nc.UPF      (For MoS₂)
│   └── S.pbe-n-nc.UPF       (For MoS₂)
│
├── 0_setup/                 ← Environment preparation
│   ├── install_qe7.4.sh
│   ├── setup_pseudo.sh
│   └── requirements.txt
│
├── 1_relax/                 ← [Practice 1] Structural optimization (vc-relax → relax)
│   ├── vc.in / re.in
│   ├── run_op.sh
│   ├── plot_qe_energy_force.py
│   └── plot_qe_stress.py
│
├── 2_scf/                   ← [Practice 2] SCF calculation
│   ├── scf.in
│   ├── run_scf.sh
│   └── plot_scf.py
│
├── 3_band/                  ← [Practice 3] Band Structure
│   ├── bands.in / bands_pp.in
│   ├── run_bands.sh
│   └── plot_bands.py
│
├── 4_dos/                   ← [Practice 4] DOS / PDOS
│   ├── nscf_dos.in / dos.in / pdos.in
│   ├── run_dos.sh
│   └── plot_dos.py
│
├── 5_scf_U/                 ← [Practice 5-1] Hubbard U SCF (by U value)
│   ├── scf.in
│   └── run_scf.sh
│
└── 5_band_U/                ← [Practice 5-2] Hubbard U Band comparison
    ├── bands.in / bands_pp.in
    ├── run_bands.sh
    └── plot_bands_U_compare.py

```

> **The `pseudo/` and `tmp*/` folders are shared at the project root.** The `pseudo_dir` and `outdir` of all input files are set to `'../pseudo/'` and `'../tmp/'`, so running them in each practice folder automatically references the shared paths. (The Hubbard U practice uses `tmp2~tmp5` for each U value).
> 
> 

---

## 0. Preparation



### 0.1 Download Practice Materials



```bash
git clone https://github.com/YHKlab/ESEC2026.git
cd ESEC2026/QE

```

### 0.2 Install QE (Conda Method)



In the practical web server environment, Quantum ESPRESSO is installed using Conda. (It takes about 2~3 minutes).

```bash
bash 0_setup/install_qe7.4.sh

```

> **Important**: After the installation is complete, you must close the terminal window and open a **New Terminal**. This is required to activate the `pw.x`, `bands.x`, `dos.x`, and `projwfc.x` commands.
> 
> 

Verification of installation:

```bash
which pw.x

```

If it is not found, manually activate the conda environment.

```bash
source ~/miniconda3/bin/activate
which pw.x

```

### 0.3 Prepare pseudopotentials and Python packages



```bash
# Check pseudopotential (Already included in the pseudo/ folder)
bash 0_setup/setup_pseudo.sh

# Install Python packages
pip install -r 0_setup/requirements.txt

```

---

## 1. [Practice 1] Structural Optimization (`vc-relax` $\rightarrow$ `relax`)



### 1.1 Overview



Structural optimization is a calculation that adjusts atomic positions and the lattice in the direction of lowering the energy. First, both the unit cell and atomic positions are optimized together using `vc-relax`, and then `relax` is performed one more time based on the final structure.

* **`vc-relax`** (`vc.in`): Simultaneous optimization of atomic positions and the unit cell.


* **`relax`** (`re.in`): Unit cell fixed, only atomic positions are optimized.


* The final coordinates from `vc.out` are automatically reflected in `re.in`.



### 1.2 Execution



```bash
cd 1_relax
bash run_op.sh

```

Execution flow:

```text
vc.in → vc.out → (Extract final coordinates) → re.in automatic update → re.out

```

Check convergence:

```bash
python3 plot_qe_energy_force.py re.out   # → re.energy_force.png
python3 plot_qe_stress.py vc.out         # → vc.stress.png

```

### 1.3 Result Interpretation



* **`re.energy_force.png`**: Shows the process of total energy and force decreasing according to the optimization step. When the force approaches zero, the atoms have reached a stable position.


* **`vc.stress.png`**: Shows the process of stress applied to the cell decreasing. When the stress approaches zero, the lattice is stabilized.



---

## 2. [Practice 2] SCF Calculation



### 2.1 Overview



The SCF (Self-Consistent Field) calculation is a process of obtaining a self-consistent ground state electronic structure by iteratively updating the electron density.

### 2.2 Execution



```bash
cd ../2_scf
bash run_scf.sh
python3 plot_scf.py

```

If the phrase `convergence has been achieved` is present in `scf.out`, it indicates normal convergence.

### 2.3 Result Interpretation



* **`scf_convergence.png`**: Shows the process of the total energy converging according to the SCF iteration. As the energy gradually decreases and flattens out (converges), it means the ground state has been accurately found. This SCF result (charge density) becomes the basis for subsequent Band and DOS calculations.



---

## 3. [Practice 3] Band Structure Calculation



### 3.1 Overview



While keeping the charge density obtained from SCF fixed, eigenvalues are calculated along the high-symmetry k-path ($\Gamma \rightarrow \text{M} \rightarrow \text{K} \rightarrow \Gamma$).

```text
SCF complete → pw.x (calculation='bands') → bands.x post-processing → Python plot

```

### 3.2 Execution



> The SCF (Practice 2) must be completed first.
> 
> 

```bash
cd ../3_band
bash run_bands.sh
python3 plot_bands.py

```

### 3.3 Result Interpretation



* **`band_structure.png`**: This is the energy-momentum (E-k) relationship of electrons. In the case of Graphene, the key feature is that the **valence band and the conduction band intersect linearly near the Fermi energy at the K point** (Dirac cone), which shows that Graphene is a zero-gap semimetal.



---

## 4. [Practice 4] DOS / PDOS Calculation



### 4.1 Overview



DOS (Density of States) is the number of electron states per energy, and PDOS (Projected DOS) breaks this down by atom/orbital.

```text
SCF complete → nscf calculation → dos.x / projwfc.x → Python plot

```

### 4.2 Execution



```bash
cd ../4_dos
bash run_dos.sh
python3 plot_dos.py

```

### 4.3 Result Interpretation



* **`dos_total.png`**: If a V-shape where the DOS goes to zero near the Fermi energy is visible, it is a semimetallic characteristic of Graphene originating from the Dirac cone.


* **`pdos_orbital.png`**: Shows that the vicinity of the Fermi energy is mainly dominated by the **C-p orbital** ($\pi$ bond), while deep energy (around $-20\text{ eV}$) is dominated by the **C-s orbital**.



---

## 5. [Practice 5] Hubbard U Test (MoS₂)



### 5.1 Overview



Standard DFT tends to underestimate the band gap of materials with d/f orbitals. The **Hubbard U** correction improves this by adding an on-site repulsion term to localized orbitals. Here, we compare the changes in the band structure by varying the U values ($0.0$, $1.5$, $3.0$, $4.5\text{ eV}$) for the **Mo-4d orbital** of MoS₂.

### 5.2 SCF Calculation (by U value)



```bash
cd ../5_scf_U
bash run_scf.sh

```

This script runs the SCF calculation 4 times, changing the U value based on `scf.in`. (Automatically adds/removes the `HUBBARD` card).

```text
U = 0.0 eV → ../tmp2/ → scf_U0.0.out   (U=0: Standard DFT without HUBBARD card)
U = 1.5 eV → ../tmp3/ → scf_U1.5.out
U = 3.0 eV → ../tmp4/ → scf_U3.0.out
U = 4.5 eV → ../tmp5/ → scf_U4.5.out

```

### 5.3 Band Calculation and Comparison



```bash
cd ../5_band_U
bash run_bands.sh
python3 plot_bands_U_compare.py

```

It reads the `tmp` folder corresponding to each U value, performs the band calculation, and overlays the results on a single graph. Each band is aligned based on the Fermi energy of the corresponding U. ($E_{\text{band}}(U) - E_F(U)$).

> The default plot range is $-2$ to $2\text{ eV}$ relative to the Fermi level. Range adjustment:
> 
> 
> ```bash
> python3 plot_bands_U_compare.py --emin -1 --emax 1
> 
> ```
> 
> 

### 5.4 Result Interpretation



* **`MoS2_bands_U_compare.png`**: Compares how the band structure changes as the U value increases in a single graph. Generally, you can observe a tendency for the **band gap to widen as U increases**, which is because the Hubbard correction rectifies the underestimated gap of the d-orbital. Selecting an appropriate U value by comparing it with experimental values is the core of DFT+U calculations.



---

## Summary of the Entire Execution Order



```bash
# 0. Environment preparation
bash 0_setup/install_qe7.4.sh     # (New terminal after installation)
bash 0_setup/setup_pseudo.sh
pip install -r 0_setup/requirements.txt

# 1. Structural optimization (Graphene)
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

# 5. Hubbard U Test (MoS₂)
cd 5_scf_U
bash run_scf.sh
cd ..
cd 5_band_U
bash run_bands.sh
python3 plot_bands_U_compare.py
cd ..

```

---

## Frequently Occurring Errors



**`pw.x: command not found`**


$\rightarrow$ This happens when the conda environment is not activated because a new terminal was not opened after installing QE.

```bash
source ~/miniconda3/bin/activate
which pw.x

```

**`data-file-schema.xml not found`**


$\rightarrow$ This happens when band/DOS/U-band calculations are executed without SCF results. Run the corresponding SCF first. (For Practice 5, run `5_scf_U` first).

**`two consecutive same k`**


$\rightarrow$ This occurs when the same k-point is entered consecutively during the `bands.x` post-processing. Remove duplicate consecutive k-points in the `K_POINTS crystal_b` path.

**`Unknown case for lda_plus_u_kind`**


$\rightarrow$ This happens when `U = 0.0` but the `HUBBARD` card is included. If U=0, you must remove the `HUBBARD` card and run standard DFT. (`5_scf_U/run_scf.sh` already handles this automatically).

**`Cannot project on zero atomic wavefunctions!` (projwfc.x)**


$\rightarrow$ This occurs when the `PP_PSWFC` block is missing in the pseudopotential. Check the UPF file in the `pseudo/` folder.
