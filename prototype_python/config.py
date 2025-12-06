'''
Handle Lattic constants and Physical-to-Lattice unit conversion
'''
import numpy as np


#------ D2Q9 LATTICE CONSTANTS -----

W = np.array([4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36])


#Direction Vectors
CX = np.array([0, 1, 0, -1, 0, 1, -1, -1, 1])
CY = np.array([0, 0, 1, 0, -1, 1, 1, -1, -1])
OPPOSITE = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6])


class SimulationConfig:
    def __init__(self, nx, ny, Ra, Pr=1.0):
        '''

        Args:
            nx, ny: Grid dims
            ra: Rayleigh number
            pr: Prandtly number (nu / alpha)
        '''

        self.nx = nx
        self.ny = ny
        self.Ra = Ra
        self.Pr = Pr

        # 1. Lattice Speed of Sound
        # c = 1/\sqrt{3} \Delta x / \Delta t
        self.cs_sq = 1.0/3.0

        # 2. Fluid Relaxation (Tau_f)
        # 0.5 is unstable
        self.tau_f = 0.6

        # 3. Kinematic Viscosity (nu)
        self.nu = (1/3)*(self.tau_f - (1/2))

        # 4. Thermal Diffusivity
        self.alpha = self.nu/self.Pr

        # 5. Thermal relaxation ()
        # Shan 1997 Eqn 10 -- One term removed (as is done in Shan)
        self.tau_g = (self.alpha / self.cs_sq ) + 0.5

        # 6. Boussinesq Force Scaling
        # Ra = GrPr, Gr = g(L_y^3)/(nu^2)
        self.Ly = self.ny #Or ny-1?
        self.buoyancy_coef = (self.Ra*self.nu**2)/(self.Pr * self.Ly**3)

        # Debug print
        print(f"--- CONFIGURATION ---")
        print(f"Grid: {nx}x{ny}")
        print(f"Ra: {Ra:.2e}, Pr: {Pr}")
        print(f"Tau Fluid (tau_1): {self.tau_f:.5f}")
        print(f"Tau Thermal (tau_2): {self.tau_g:.5f}")
        print(f"Buoyancy Coef: {self.buoyancy_coef:.5e}")
        print(f"---------------------")
