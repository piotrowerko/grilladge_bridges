import numpy as np
from PyNite.FEModel3D import FEModel3D
from grilladge import Grilladge

class GrillModel(FEModel3D):
    """Instance of this class is a Grilladge FE model,
    build on basis of instance of Grilladge class instance from grilladge module"""
    def __init__(self,
                 name, 
                 no_of_beams=2, 
                 beam_spacing=8, 
                 span_data=(2, 30, 30),
                 canti_l=2.5,
                 skew=90,
                 discr=2,
                 tr_discr=3):
        #  https://www.youtube.com/watch?v=MBbVq_FIYDA
        super().__init__()
        self.name = name
        self.grilladge = Grilladge(no_of_beams, 
                                   beam_spacing, 
                                   span_data,
                                   canti_l,
                                   skew)
        self.grill_coors = self.grilladge.grilladge_nodes_c(discr, 
                                                         tr_discr)
        
    def __str__(self):
        return f'{self.name}'
    
    def add_nodes(self, no_to_disp=1.0):
        node_data = self.grilladge.add_name(self.grill_coors)
        for el in node_data:
            self.add_node(*el)
        #self.add_node('ppp', 1, 1 , 1)
        #return self.Nodes[7.0].X, self.Nodes[7.0].Y, self.Nodes[7.0].Z
        #return node_data
        return self.Nodes[no_to_disp].X, self.Nodes[no_to_disp].Y, self.Nodes[no_to_disp].Z
        #return type(self.Nodes)
    #  Unpacking Dictionaries With the ** Operator
    # https://stackabuse.com/unpacking-in-python-beyond-parallel-assignment/
    
    def girders(self, name, i_node=1, j_node=2, E=1, G=1, 
                Iy=1, Iz=1, J=1, A=1, auxNode=None,
                tension_only=False, comp_only=False):
        self.add_member
        return None

    # def add_member(self, name, i_node, j_node, E, G, Iy, Iz, J, A, auxNode=None,
    #                tension_only=False, comp_only=False):

def main():
    wd185 = GrillModel('wd_185')
    # print(wd185._z_coors_of_cantitip(discr=10, edge=2))
    # print(wd185._z_coors_in_g(discr=10, gird_no=2))
    # print(wd185._x_coors_in_g1(discr=10))
    # print(wd185._x_coors_in_g(discr=10, gird_no=2))
    #print(wd185.grill_coors)
    print(wd185.add_nodes())
    
if __name__ == '__main__':
    main()