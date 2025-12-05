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
    def __init__(self, nx, ny, ra, pr=1.0);
        #TODO
