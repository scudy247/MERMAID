# MERMAID

**M**ulti-arm**E**d bandit approach fo**R** opti**M**al c**A**rrier selection **I**n OFDM-based un**D**erwater acoustic networks

MERMAID is a lightweight framework for **adaptive OFDM subcarrier selection** in Underwater Acoustic Networks (UANs). It uses a **Combinatorial Multi-Armed Bandit (CMAB)** with an Upper Confidence Bound (UCB) policy. The agent picks which subset of subcarriers to activate based on real-time **Packet Delivery Ratio (PDR)** feedback, aiming to maximize reliability while keeping energy consumption low.

This repository contains:

- the simulation code: Python agents and the DESERT/NS-Miracle TCL scenario;
- the exported results of the training runs;
- the MATLAB scripts that produce the figures in the paper ([`MERMAID.pdf`](MERMAID.pdf)).

---

## Highlights

The paper compares MERMAID with two Deep Reinforcement Learning baselines (DDQN and PPO) on a point-to-point OFDM link simulated in DESERT:

| Metric | MERMAID | DDQN | PPO |
|---|---|---|---|
| Average PDR | **44.37 %** | 35.02 % | 23.22 % |
| Energy per delivered packet | **1.01 J/pkt** | 1.24 J/pkt | 1.85 J/pkt |
| Episodes in which all 3 good subcarriers are selected | **94.5 %** | 31.1 % | 1.6 % |

- MERMAID delivers up to **21.15 % more PDR** and uses up to **45.40 % less energy per delivered packet** than the DRL baselines.
- It gets close to the highest PDR possible in this scenario (45.71 %) and converges within a few episodes.
- It needs no prior training, no neural networks, and very little memory, so it suits resource-constrained IoUT nodes.

---

## How it works

```
 ┌────────────────────┐   carrier mask (8 bits)   ┌───────────────────────────┐
 │  Python agent      │ ────────────────────────▶ │  DESERT / NS-Miracle      │
 │  (CMAB / DDQN /    │   ns newSimulation.tcl    │  OFDM-ALOHA scenario      │
 │   PPO)             │       c0 c1 ... c7        │  (one 300 s episode)      │
 │                    │ ◀──────────────────────── │                           │
 └────────────────────┘     rewards.csv           └───────────────────────────┘
          │               "PDR, energy"
          ▼
   Weights & Biases logging (pdr, reward, energy, selected carriers)
```

1. **Arms.** Each of the `N = 8` OFDM subcarriers is a base arm. A *super arm* is the subset of `K` subcarriers that are active during one episode.
2. **Episode.** The agent picks a subset. The Python driver then launches [`newSimulation.tcl`](Codes/newSimulation.tcl) with an 8-element binary carrier mask, where `1` means the carrier is enabled. One simulation is one episode of `Δ = 300 s`.
3. **Reward.** At the end of the run, the TCL script writes `PDR, energy` to `rewards.csv` in the working directory (the file is created at runtime). The driver reads this file back and uses the PDR as the reward.
4. **Update.** The agent updates its statistics and picks the next subset.

### CMAB-UCB policy

The agent keeps, for each subcarrier `s`, an empirical mean reward and a selection counter `N(s)`. At episode `n` it activates the `K` subcarriers with the highest UCB index:

```
UCB(s) = mean_reward(s) + sqrt( c · ln(n) / N(s) ),   c = 2
```

A subcarrier that has never been tried gets an infinite index, which forces some exploration at the start. Before the UCB phase begins, the driver also runs a warm-up that tries **every** one of the `C(8, K)` combinations once.

### Baselines

- **DDQN** ([`ddqn_fixed_subset.py`](Codes/ddqn_fixed_subset.py)): a Double Deep Q-Network with these settings:
  - a 2×128 MLP;
  - experience replay with a buffer of 10 000 and a batch size of 64;
  - a target network synced every 20 steps;
  - ε-greedy exploration, decaying from 1.0 to 0.05.

  Each action is one of the `C(8, K)` subsets.
- **PPO** ([`ppo_fixed_subset.py`](Codes/ppo_fixed_subset.py)): Proximal Policy Optimization with separate 2×64 policy and value networks, a clipped surrogate objective (`ε = 0.2`), and a categorical policy over the `C(8, K)` subsets.

---

## Simulation scenario

These are the settings in [`Codes/newSimulation.tcl`](Codes/newSimulation.tcl):

| Parameter | Value |
|---|---|
| Simulator | DESERT Underwater (NS-2 + NS-Miracle) |
| Topology | 1 transmitter → 1 sink, plus 1 interfering node |
| Carrier frequency / bandwidth | 125 kHz / 125 kHz |
| OFDM subcarriers | 8 (about 15.6 kHz each) |
| Selected subcarriers `K` | 3 in the paper (the driver scripts sweep 3 to 8) |
| Bit rate | 64 kbps |
| MAC | OFDM-ALOHA |
| Modulation | BPSK |
| Max Tx SPL | 130 dB re 1 µPa |
| Traffic | Poisson CBR, 460 B packets |
| Episode length | 300 s |
| Episodes per run | 1000 |

The interfering node transmits on every subcarrier **except** indices `2`, `4` and `7` (0-based). Subcarriers **3, 5 and 8** (1-based) are therefore the only good channels, and selecting them is the optimal action.

---

## Repository structure

```
MERMAID/
├── MERMAID.pdf                          # Paper
├── Codes/
│   ├── combinatorial_fixed_subset.py    # CMAB-UCB agent (MERMAID)
│   ├── ddqn_fixed_subset.py             # DDQN baseline agent
│   ├── ppo_fixed_subset.py              # PPO baseline agent
│   ├── main_combinatorial_fixed.py      # Training loop: MERMAID ↔ DESERT
│   ├── main_ddqn_fixed.py               # Training loop: DDQN ↔ DESERT
│   ├── main_ppo_fixed.py                # Training loop: PPO ↔ DESERT
│   └── newSimulation.tcl                # DESERT OFDM scenario (takes an 8-bit carrier mask)
└── Plots/
    ├── Plot_Figures.m                   # Plots Figs. 2–4 of the paper
    ├── Subcarrier_Accuracy.m            # Builds Table I (subcarrier-selection accuracy)
    ├── Combinatorial_MAB/               # Exported logs for MERMAID (pdr, reward, energy, action0–2) as .xlsx
    ├── DDQN/                            # Exported logs for DDQN
    ├── PPO/                             # Exported logs for PPO
    ├── Cumulative_Reward.pdf            # Fig. 2
    ├── Average_PDR.pdf                  # Fig. 3
    ├── Energy_per_packet.pdf            # Fig. 4
    ├── Accuracy_Table.png               # Table I
    └── hatchfill2.m, legendflex.m, getpos.m   # Third-party plotting helpers
```

---

## Requirements

- **Linux** (tested on Ubuntu and WSL).
- **[DESERT Underwater](https://github.com/uwsignet/DESERT_Underwater)** with NS-2 and NS-Miracle, built with the OFDM modules (`libuwofdmphy`, `libuwofdmaloha`, `libuwinterferenceofdm`). The `ns` executable must be on your `PATH`.
- **Python 3.8 or later**, with these packages:
  ```bash
  pip install numpy torch wandb
  ```
- **MATLAB** (optional), only to regenerate the figures.

---

## Usage

All commands below are run from the repository root. Every path is relative.

### 1. Weights & Biases (optional)

The training scripts log to W&B with `project="combinatorial_ucb"` and `entity="uwa"`. To keep logging, log in and change `entity` to your own account:

```bash
wandb login
```

To turn logging off, set `log_wandb = False` at the top of each `main_*.py` script.

### 2. Run an agent

The driver calls `ns newSimulation.tcl …`, and the scenario writes `rewards.csv` to the current directory, so run the scripts from inside `Codes/`:

```bash
cd Codes
python main_combinatorial_fixed.py   # MERMAID (CMAB-UCB)
python main_ddqn_fixed.py            # DDQN baseline
python main_ppo_fixed.py             # PPO baseline
```

Each script loops over the subset sizes `K ∈ {3, …, 8}` and runs 1000 episodes for each one. Every episode is a full 300 s DESERT simulation, so expect a long runtime: the paper reports about 90 minutes per training run.

### 3. Run a single simulation manually

```bash
cd Codes
ns newSimulation.tcl 0 0 1 0 1 0 0 1   # enable subcarriers 3, 5 and 8
cat rewards.csv                          # → "<PDR>, <energy>"
```

### 4. Test the agents without DESERT

The CMAB and DDQN agent files each contain a small stand-alone demo that uses synthetic Bernoulli rewards:

```bash
cd Codes
python combinatorial_fixed_subset.py
python ddqn_fixed_subset.py
```

### 5. Reproduce the figures

In MATLAB, set `Plots/` as the current folder and run:

```matlab
Plot_Figures          % Figs. 2–4
Subcarrier_Accuracy   % Table I
```

Both scripts read the `.xlsx` logs from the `Combinatorial_MAB/`, `DDQN/` and `PPO/` sub-folders through relative paths.

---

## Citation

If you use this code, please cite:

```bibtex
@article{mermaid,
  title   = {{MERMAID}: a Multi-armEd bandit approach foR optiMal cArrier selection In {OFDM}-based unDerwater acoustic networks},
  author  = {Busacca, Fabio and Galluccio, Laura and Palazzo, Sergio and Panebianco, Andrea and Raftopoulos, Raoul and Scuderi, Dario},
  year    = {2025}
}
```

---

## Authors

Fabio Busacca, Laura Galluccio, Sergio Palazzo, Andrea Panebianco, Raoul Raftopoulos, Dario Scuderi

University of Catania · University of Palermo · CNIT Catania Research Unit, Italy

## Acknowledgments

This work was partially supported by the European Union under the Italian National Recovery and Resilience Plan (NRRP) of NextGenerationEU, partnership on "Telecommunications of the Future" (PE0000001 – program "RESTART").

The simulations are built on the [DESERT Underwater](https://github.com/uwsignet/DESERT_Underwater) framework.
