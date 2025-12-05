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
        # TODO
        self.cfg = cfg
        self.shape = (9, cfg.ny, cfg.nx)

        # Populations
        self.f = np.zeros(self.shape) # Fluid
        self.g = np.zeros(self.shape) # Thermal

        # Macroscopic
        self.rho = np.ones((cfg.ny, cfg.nx))
        self.u   = np.ones((2,cfg.ny, cfg.nx)) #0=u_x, 1=u_y
        self.T   = np.zeros((cfg.ny, cfg.nx))

        # Buffers
        self.feq = np.zeros(self.shape) # Fluid
        self.geq = np.zeros(self.shape) # Thermal

    def initialize(self):
        #TODO: What do they do in the paper?


    def compute_equilibrium(self, rho, u, type='fluid'):
        '''D2Q9 Equilibrium expansion (Eqn 2 Shan 1997) '''
        ea_dot_u = 3.0 * (CX[:, None, None] * u[0] + CY[:, None, None] * u[1])
        u_dot_u = 1.5 * (u[0]**2 + u[1]**2)

        return rho*W[:, None, None] * 1.0 + ea_dot_u + 0.5 * ea_dot_u**2 - u_dot_u)


    def collide(self):
        #Macroscopic moments (Shan 1997 between Eqn 1 and 2)
        self.rho = np.sum(self.f, axis = 0)
        self.T   = np.sum(self.g, axis = 1)

        inv_rho = 1.0 / self.rho
        self.u[0] = np.sum(self.f * CX[:, None, None], axis = 0) * inv_rho
        self.u[1] = np.sum(self.f * CY[:, None, None], axis = 0) * inv_rho

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
        self.geq = self.compute_equilibrium(self.T, u_eq_g, type = 'fluid')

        # 5. Relax (compute RHS)
        self.f += -(1.0 / self.cfg.tau_f) * (self.f - self.feq)
        self.g += -(1.0 / self.cfg.tau_g) * (self.g - self.geq)




    def stream(self):
        # LHS of Eq (1): n(x + e)
        for i in range(9):
            self.f[i] = np.roll(self.f[i], (CX[i], CY[i]), axis=(1, 0))
            self.g[i] = np.roll(self.g[i], (CX[i], CY[i]), axis=(1, 0))

    def apply_bcs(self):
        #TODO

        raise Exception()

    def step(self):
        #f(t) (post collision) -> stream (f(t+1)) -> collide (f(t+1) post collision)
        self.stream()
        self.apply_bcs()
        self.collide()
