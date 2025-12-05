# High-Performance Lattice-Boltzmann Solver (LBM)

![Status](https://img.shields.io/badge/Status-Active_Development-green)
![Tech](https://img.shields.io/badge/Stack-CUDA_%7C_C%2B%2B_%7C_MPI-blue)

A performance engineering study targeting simulation of Rayleigh-Bénard Convection at $Ra = 10^{13}$.

This project iteratively optimises a LBM (CFD) solver from a Python prototype to a distributed multi-GPU implementation. It serves as a practical application of the book **"Programming Massively Parallel Processors" (PMPP)**, which is being read in tandem to the development of this project, applied to scientific computing.

## Engineering Roadmap

The project aims to saturate GPU Memory Bandwidth (Track 1) to enable high-fidelity turbulence modeling (Track 2) at scale (Track 3).

This is the current expected pathway, but we expect this may change as the project progresses. This README will represent the most up-to-date info on the project.

### Track 1: Hardware Acceleration (The PMPP Strategy)
*Goal: Saturate the GPU Memory Bandwidth (Roofline) and hide latency.*

*   [ ] **Phase I: Baseline & I/O.**
    *   Establish C++ serial baseline and binary I/O formats for verification.
*   [ ] **Phase II: Naive CUDA Port.**
    *   Direct translation of loops to threads to establish the baseline.
    *   *Target:* Identify Uncoalesced Global Memory bottlenecks.
*   [ ] **Phase III: Memory Coalescing.**
    *   Transition data layout from Array of Structures to **Structure of Arrays (SoA)**.
    *   *Reference:* PMPP Ch. 4 (Memory and Data Locality).
*   [ ] **Phase IV: Shared Memory Tiling.**
    *   Implement halo-caching in Shared Memory to mitigate the 9-point stencil memory traffic.
    *   *Reference:* PMPP Ch. 5 (Tiling).
*   [ ] **Phase V: Compute Optimization.**
    *   Register shuffling and loop unrolling to maximize instruction throughput once bandwidth is saturated.
    *   *Reference:* PMPP Ch. 18.

### Track 2: Physics & Fidelity
*Goal: Numerical stability for high Rayleigh numbers ($Ra > 10^{13}$).*

*   [ ] **Phase I: Python Prototype (Validation).**
    *   Implementation of the **Shan (1997)** Double Distribution model.
    *   *Validated:* Boussinesq coupling and critical Nusselt numbers ($Ra_c \approx 1708$).
*   [ ] **Phase II: Stability -- Hybrid Recursive Regularization (HRR).**
    *   Implementation of the **Farag (2020)** model.
    *   *Why:* Standard BGK LBM is unstable at high Reynolds numbers. HRR filters non-equilibrium modes to prevent crash.
    *   This algorithmic change is expected to increase arithmetic intensity, potentially requiring a re-evaluation of Track 1 optimizations.

### Track 3: Scale-Out
*Goal: Domain Decomposition for 8K resolution ($7680 \times 4320$).*

*   [ ] **Phase I: Multi-GPU Architecture.**
    *   Domain decomposition implementation.
    *   *Why:* Verifies domain decomposition logic.
*   [ ] **Phase II: CUDA-Aware MPI.**
    *   Halo exchange implementation using direct GPU-to-GPU communication.
*   [ ] **Phase III: Communication Hiding.**
    *   Overlapping MPI communication with inner-domain kernel computation.
    *   *Why:*  Allow asynchrononous computation of inner and boundary

## 🏗️ Architecture

The project maintains parallel implementations to allow for rigorous A/B performance benchmarking and correctness verification.

```text
/
├── prototype_python/       # Reference physics implementation (Physics Ground Truth)
├── src_cpp/                # The HPC Engine
│   ├── kernels/            # Evolution of CUDA Kernels (Naive -> SoA -> Shared)
│   ├── comms/              # MPI Halo Exchange logic
│   └── solver/             # C++ Driver code
├── viz/                    # Python-based visualization pipeline
└── benchmarks/             # Automated verification & speedup regression tests
```
