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

        raise Exception('Not functional for temperatures yet')

        return rho*W[:, None, None] * 1.0 + ea_dot_u + 0.5 * ea_dot_u**2 - u_dot_u)


    def collide(self):
        #Macroscopic moments
        #TODO

    def stream(self):
        #TODO

    def apply_bcs(self):
        #TODO

    def step(self):
        self.collide()
        self.stream()
        self.apply_bcs()
