import numpy as np
from .config import W, CX, CY

class ShanLBMSolver:
    """
    Implements the Shan (1997) Double Distribution Function model.

    Manages two populations:
    1. Fluid (f): Navier-Stokes via BGK collision.
    2. Thermal (g): Advection-Diffusion via BGK collision.

    Coupling is achieved via the Boussinesq approximation acting on the
    Equilibrium Velocity of the Fluid population.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.shape = (9, cfg.ny, cfg.nx)

        # Populations
        self.f = np.zeros(self.shape) # Fluid
        self.g = np.zeros(self.shape) # Thermal

        # Macroscopic
        self.rho = np.ones((cfg.ny, cfg.nx))
        self.u   = np.zeros((2,cfg.ny, cfg.nx)) #0=u_x, 1=u_y
        self.T   = np.zeros((cfg.ny, cfg.nx))

        # Buffers
        self.feq = np.zeros(self.shape) # Fluid
        self.geq = np.zeros(self.shape) # Thermal

    def initialize(self):
        # Initialize with steady state (analytical solution) with a perturbation
        for y in range(self.cfg.ny):
            self.T[y,:] = 1.0 - (y / (self.cfg.ny))

        # Perturbation (1% of total value)
        epsilon = 0.1

        # Create grid of coordinates
        x = np.arange(self.cfg.nx)
        y = np.arange(self.cfg.ny)
        X, Y = np.meshgrid(x, y)

        perturbation = epsilon * (np.sin(np.pi * X / (self.cfg.nx - 1)) * \
                                  np.sin(np.pi * Y / (self.cfg.ny - 1)))
        self.T += perturbation

        #Initialize as equilibrium value
        self.f[:] = self.compute_equilibrium(self.rho, self.u, type = 'fluid')
        self.g[:] = self.compute_equilibrium(self.T, self.u, type = 'thermal')


    def compute_equilibrium(self, rho, u, type='fluid'):
        '''D2Q9 Equilibrium expansion (Eqn 2 Shan 1997) '''
        ea_dot_u = 3.0 * (CX[:, None, None] * u[0] + CY[:, None, None] * u[1])
        u_dot_u = 1.5 * (u[0]**2 + u[1]**2)

        return rho*W[:, None, None] * (1.0 + ea_dot_u + 0.5 * ea_dot_u**2 - u_dot_u)


    def collide(self):
        #Macroscopic moments (Shan 1997 between Eqn 1 and 2)
        self.rho = np.sum(self.f, axis = 0)
        self.T   = np.sum(self.g, axis = 0)

        inv_rho = 1.0 / self.rho
        self.u[0] = np.sum(self.f * CX[:, None, None], axis = 0) * inv_rho
        self.u[1] = np.sum(self.f * CY[:, None, None], axis = 0) * inv_rho

        # -- No-slip BC Enforcement --
        #Force before equilibrium computation
        self.u[:, 0, :] = 0.0
        self.u[:, -1, :] = 0.0

        # 2. Calculate Boussinesq (Gravity force -- Shan 1997 Eqn 12)
        y_grid = np.arange(self.cfg.ny)[:,None]
        #  Coordinates center of domain (e.g. y \in [-.5,.5])
        linear_profile =  1.0 - (y_grid / (self.cfg.ny - 1))

        #TODO: Define buoyancy coeff
        g_eff_y = self.cfg.buoyancy_coef * (self.T - linear_profile)

        # 3. Calculate equilibrium Velocity
        #   'u is replaced by u1 + tau_sigma * g for both components' (Shan 1997 pg 6)
        # Component 1: Fluid
        u_eq_f = self.u.copy()
        u_eq_f[1] += self.cfg.tau_f*g_eff_y

        # Component 2: Thermal
        u_eq_g = self.u.copy()
        u_eq_g[1] += self.cfg.tau_g*g_eff_y

        # 4. Calculate Equilibrium distributions
        self.feq = self.compute_equilibrium(self.rho, u_eq_f, type = 'fluid')
        self.geq = self.compute_equilibrium(self.T, u_eq_g, type = 'thermal')

        # 5. Relax (compute RHS)
        self.f += -(1.0 / self.cfg.tau_f) * (self.f - self.feq)
        self.g += -(1.0 / self.cfg.tau_g) * (self.g - self.geq)




    def stream(self):
        # LHS of Eq (1): n(x + e)
        for i in range(9):
            self.f[i] = np.roll(self.f[i], (CX[i], CY[i]), axis=(1, 0))
            self.g[i] = np.roll(self.g[i], (CX[i], CY[i]), axis=(1, 0))

    def apply_bcs(self):
        # ----- FLUID BC (No-slip) -----
        # Shan 1997 Eqn 14

        # Bottom Wall (y=0): n_+^0 (2,5,6) unknown
        # Set them with n_-^0 (4,7,8)
        self.f[2, 0, :] = self.f[4, 0, :]
        self.f[5, 0, :] = self.f[7, 0, :]
        self.f[6, 0, :] = self.f[8, 0, :]

        # Top wall (y=n_y): n_-^{n_y} (4,7,8) unknown
        # Set them with n_+^{n_y} (2,5,6)
        self.f[4, -1, :] = self.f[2, -1, :]
        self.f[7, -1, :] = self.f[5, -1, :]
        self.f[8, -1, :] = self.f[6, -1, :]



        # ----- TEMP BC (Isothermal) -----
        # Shan 1997 Eqn 17: n_a = 2*w_a*T_wall - n_b

        # Bottom Wall (y=0, T=1.0):
        t_wall_bot = 1.0
        self.g[2, 0, :] = 2 * W[2] * t_wall_bot - self.g[4, 0, :]
        self.g[5, 0, :] = 2 * W[5] * t_wall_bot - self.g[7, 0, :]
        self.g[6, 0, :] = 2 * W[6] * t_wall_bot - self.g[8, 0, :]

        # Top Wall (y=-1, T=0.0):
        t_wall_top = 0.0
        self.g[4, -1, :] = 2 * W[4] * t_wall_top - self.g[2, -1, :]
        self.g[7, -1, :] = 2 * W[7] * t_wall_top - self.g[5, -1, :]
        self.g[8, -1, :] = 2 * W[8] * t_wall_top - self.g[6, -1, :]


    def step(self):
        #f(t) (post collision) -> stream (f(t+1)) -> collide (f(t+1) post collision)
        self.stream()
        self.apply_bcs()
        self.collide()
