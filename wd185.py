# Import 'FEModel3D' and 'Visualization' from 'PyNite'
# from PyNiteFEA import FEModel3D
# from PyNite import Visualization

import numpy as np
from PyNite.FEModel3D import FEModel3D
from grilladge import Grilladge

# from PyNite import Grilladge

# Create a new model
wd185_fe = FEModel3D()
wd185_coor = Grilladge(no_of_beams=2, beam_spacing=8, span_data=(2, 30, 30), skew=90)
# print(wd185._z_coors_of_cantitip(discr=10, edge=2))
# print(wd185._z_coors_in_g(discr=10, gird_no=2))
# print(wd185._x_coors_in_g1(discr=10))
# print(wd185._x_coors_in_g(discr=10, gird_no=2))
nodes_coors = wd185_coor._nodes_coor(discr=2, tr_discr=3)

# Define the nodes
print(wd185_fe.add_node(1, 0, 0, 0))
print(wd185_fe.add_node(2, 1, 0, 0))
