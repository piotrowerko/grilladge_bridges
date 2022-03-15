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
                 tr_discr=4):
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
        __list = [i for i in range(21)]
        _b_list = [22, 24, 25, 27, 29, 30, 32, 34]
        #__list.append(25, 30)
        __list += _b_list
        print(__list)
        for el in node_data[__list]:
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
            self.add_member((i+1), self.Nodes[(j+i+1)*1.0].Name, 
                            self.Nodes[((j+i+2)*1.0)].Name, E, G, Iy, Iz, J, A, 
                            auxNode=None,
                            tension_only=False, 
                            comp_only=False)
        return self.Members

    def add_deck_trans(self, E=35000000, G=16000000, 
                Iy=0.1, Iz=0.1, J=0.1, A=0.1, auxNode=None,
                tension_only=False, comp_only=False):
        """adds FE members representing bridge deck in trans. direction"""
        _jj = int(self.discr * self.grilladge.span_data[0] * self.no_of_beams + self.no_of_beams)  # _no_of_main_gird_fe + 2 
        _number = int(self.discr * self.grilladge.span_data[0] + 1) # no of cantilevel FE on one side + 1
        _kk = (self.no_of_beams - 1) * (_number) + 1  # number of first node in last girder
        for i in range(0, _number, 1):
            # adding cantilevel FE - bottom egde:
            self.add_member((_jj+i-1), self.Nodes[(i+1)*1.0].Name, self.Nodes[((_jj+i+1)*1.0)].Name, 
                            E, G, Iy, Iz, J, A, 
                            auxNode=None,
                            tension_only=False, 
                            comp_only=False)
            # adding cantilevel FE - upper egde:
            self.add_member((_jj-1+_number+i), self.Nodes[(_kk+i)*1.0].Name, self.Nodes[((_jj+_kk+i)*1.0)].Name, 
                            E, G, Iy, Iz, J, A, 
                            auxNode=None,
                            tension_only=False, 
                            comp_only=False)
            # add FE members representing bridge deck in trans. direction:
        return self.Members
    
    def add_cross_members(self, E=35000000, G=16000000, 
                Iy=1, Iz=1, J=1, A=1, auxNode=None,
                tension_only=False, comp_only=False):
        """adds FE members representing cross members"""
        _number_tot = int(self.discr * self.grilladge.span_data[0] * self.no_of_beams)
        _number = int(self.discr * self.grilladge.span_data[0])
        _pp = _number_tot + self.no_of_beams + 2 * _number + 2  # number of nodes in longitudinal members
        
        for j in range(self.grilladge.span_data[0] + 1):
            _last_mem_no = list(self.Members.keys())[-1]
            self.add_member((_last_mem_no+1), self.Nodes[j * self.discr + 1].Name, self.Nodes[j * self.discr + _pp + 1].Name, 
                                E, G, Iy, Iz, J, A, 
                                auxNode=None,
                                tension_only=False, 
                                comp_only=False)

            for i in range(self.tr_discr-2):
                self.add_member((i+_last_mem_no+2), 
                                self.Nodes[j * self.discr + (_number + 1) * i + _pp + 1].Name, 
                                self.Nodes[j * self.discr + (_number + 1) * i + _pp + _number + 2].Name, 
                                E, G, Iy, Iz, J, A, 
                                auxNode=None,
                                tension_only=False, 
                                comp_only=False)

            _last_mem_no = list(self.Members.keys())[-1]
            _curr_node = self.Members[_last_mem_no].j_node.Name
            self.add_member((_last_mem_no+1), _curr_node, self.Nodes[j * self.discr + _number + 2].Name, 
                        E, G, Iy, Iz, J, A, 
                        auxNode=None,
                        tension_only=False, 
                        comp_only=False)
        return _last_mem_no, _pp

def main():
    wd185 = GrillModel('wd_185')

    wd185.add_nodes()
    wd185.add_girders()
    wd185.add_deck_trans()

    print(wd185.add_cross_members())
    
    # Define the supports
    
    wd185.def_support(1.0, *(6 * [True]))
    wd185.def_support(5.0, *(6 * [True]))
    wd185.def_support(6.0, *(6 * [True]))
    wd185.def_support(10.0, *(6 * [True]))

    # Add nodal loads
    wd185.add_node_load(2.0, 'FY', -400)
    
    # Analyze the model
    wd185.analyze(check_statics=False)
    
    # Render the deformed shape
    Visualization.render_model(wd185, annotation_size=0.2, deformed_shape=True, deformed_scale=200, render_loads=True)
    
if __name__ == '__main__':
    main()