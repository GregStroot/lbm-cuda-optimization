# System Architecture

## File Organization
The codebase separates the Reference Logic (Python) from the High-Performance Engine (C++).

### Prototype (Python)
- `config.py`: Centralized parameter conversion. Converts physical units ($Ra, Pr$) to lattice units ($\nu, \tau$).
- `lbm_solver.py`: The `ShanLBMSolver` class. Contains the main time-stepping loop and memory allocation.
