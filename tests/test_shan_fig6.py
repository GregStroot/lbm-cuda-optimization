from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from prototype_python.config import SimulationConfig
from prototype_python.lbm_solver import ShanLBMSolver


def get_nusselt(Ra_val):
    cfg = SimulationConfig(nx = 101, ny = 50, Ra=Ra_val, Pr =0.71)
    solver = ShanLBMSolver(cfg)
    solver.initialize()

    # Run to steady state (
    print(f"Running Ra={Ra_val}...")
    for i in tqdm(range(80000)):
        solver.step()

        if (i % 1000 == 0 and i > 9000):
            plt.imshow(solver.T)
            plt.colorbar()
            plt.show()
            if (i > 10000):
                T_diff = np.sum(solver.T - T_prev)
                print(f"T_diff: {T_diff}")
                T_prev = solver.T
            else:
                T_prev = solver.T

    # Calculate Nusselt
    # Nu = 'Total heat transfer'/'Conductive heat transfer'
    # Average convective heat flux
    avg_conv = np.mean(solver.u[1] * solver.T)

    # Reference conductive heat flux (over entire domain)
    cond_flux = solver.cfg.alpha * ( 1.0 / solver.cfg.Ly)

    Nu = 1.0 + (avg_conv / cond_flux)

    return Nu

def reproduce_fig():
    #Shan 1997 does more than this, but start here
    #Ra_values = [2000, 2500, 3000, 5000, 10000, 20000]
    Ra_values = [10000]
    Nu_results = []

    for Ra in Ra_values:
        Nu = get_nusselt(Ra)
        Nu_results.append(Nu)
        print(f"Ra={Ra} => Nu={Nu:.3f}")

    Nu_fit = 1.56*np.array(Ra_values)**0.296

    plt.figure(figsize=(6,6))
    plt.plot(Ra_values, Nu_results, 'rs-', label = 'Current LBM (Shan 1997)')
    plt.xlabel(r'$Ra$')
    plt.ylabel(r'$Nu$')
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    reproduce_fig()
