import numpy as np
from PyNite.FEModel3D import FEModel3D
from grilladge import Grilladge
from PyNite import Visualization

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
        self.discr = discr
        self.tr_discr = tr_discr
        self.no_of_beams = no_of_beams

    def __str__(self):
        return f'{self.name}'
    
    def add_nodes(self, no_to_disp=1.0):
        node_data = self.grilladge.add_name(self.grill_coors)
        for el in node_data[0:10]:
            self.add_node(*el)
        #return self.Nodes[no_to_disp].Name, self.Nodes[no_to_disp].X, self.Nodes[no_to_disp].Y, self.Nodes[no_to_disp].Z
        return list(self.Nodes[no_to_disp])  # this will only run when Node 3D class in pynite is changed
        #return type(self.Nodes)
    #  Unpacking Dictionaries With the ** Operator
    # https://stackabuse.com/unpacking-in-python-beyond-parallel-assignment/
    
    def add_girders(self, E=35000000, G=16000000, 
                Iy=1, Iz=1, J=1, A=1, auxNode=None,
                tension_only=False, comp_only=False):
        """adds FE members representing bridge main deck girders"""
        _number_tot = int(self.discr * self.grilladge.span_data[0] * self.no_of_beams)
        _number = int(self.discr * self.grilladge.span_data[0])
        j = 0
        for i in range(0, _number_tot, 1):
            if i % _number == 0 and i > 0:
                j += 1
            self.add_member((i+1)*1.0, self.Nodes[(j+i+1)*1.0].Name, self.Nodes[((j+i+2)*1.0)].Name, E, G, Iy, Iz, J, A, 
                            auxNode=None,
                            tension_only=False, 
                            comp_only=False)

        # for i in range(_number+1, 2*_number, 1):
        #     self.add_member((i+1)*1.0, self.Nodes[(i+1)*1.0].Name, self.Nodes[((i+2)*1.0)].Name, E, G, Iy, Iz, J, A, 
        #                     auxNode=None,
        #                     tension_only=False, 
        #                     comp_only=False)
    
        #frame.add_member('M1', 'N1', 'N2', E, G, Iy, Iz, J, A)
        return self.Members

    # def add_member(self, name, i_node, j_node, E, G, Iy, Iz, J, A, auxNode=None,
    #                tension_only=False, comp_only=False):

def main():
    wd185 = GrillModel('wd_185')
    # print(wd185._z_coors_of_cantitip(discr=10, edge=2))
    # print(wd185._z_coors_in_g(discr=10, gird_no=2))
    # print(wd185._x_coors_in_g1(discr=10))
    # print(wd185._x_coors_in_g(discr=10, gird_no=2))
    #print(wd185.grill_coors)
    wd185.add_nodes()
    wd185.add_girders()
    
    wd185.add_member(9.0, 3.0, 8.0, 35000000, 16000000, 1, 1, 1, 1)
    print(wd185.Members)
    print(list(wd185.Members[9.0].i_node))
    
    # Define the supports
    wd185.def_support(1.0, True, True, True, True, True, True)
    wd185.def_support(5.0, True, True, True, True, True, True)
    wd185.def_support(6.0, True, True, True, True, True, True)
    wd185.def_support(10.0, True, True, True, True, True, True)

    # Add nodal loads
    wd185.add_node_load(2.0, 'FY', -400)
    
    # Analyze the model
    wd185.analyze(check_statics=False)
    
    # Render the deformed shape
    Visualization.render_model(wd185, annotation_size=0.5, deformed_shape=True, deformed_scale=200, render_loads=True)
    
if __name__ == '__main__':
    main()