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
                 beam_spacing=4, 
                 span_data=(2, 30, 30),
                 canti_l=2.5,
                 skew=-60,
                 discr=10,
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
        # __list = [i for i in range(21)]
        # _b_list = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
        # #__list.append(25, 30)
        # __list += _b_list
        # print(__list)
        __list = [i for i in range(len(node_data))]
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

    def add_deck_trans_can(self, E=35000000, G=16000000, 
                Iy=0.1, Iz=0.1, J=0.1, A=0.1, auxNode=None,
                tension_only=False, comp_only=False):
        """adds FE members representing bridge cantilevels in trans. direction"""
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
    
    def add_cross_members_(self, E=35000000, G=16000000, 
                Iy=1, Iz=1, J=1, A=1, auxNode=None,
                tension_only=False, comp_only=False, deck=False):
        """adds FE members representing cross members or bridge deck in trans. dir."""
        _number_tot = int(self.discr * self.grilladge.span_data[0] * self.no_of_beams)
        _number = int(self.discr * self.grilladge.span_data[0])
        _pp = _number_tot + self.no_of_beams + 2 * _number + 2  # number of nodes in longitudinal members + cantiENDs nodes
        
        # adding _loop variables for creation of additional trans. bars repr. deck in trans. dir.:
        if deck == True:
            _first_loop = self.grilladge.span_data[0]  # eq. to number of spans
            _sec_loop = int(self.discr) - 1  # eq. to number of cross lines of deck cross bars in each span
        else:
            _first_loop = self.grilladge.span_data[0] + 1  # eq. to number of support cross members
            _sec_loop = 1
        
        for j in range(_first_loop):
            for k in range(_sec_loop):
                _last_mem_no = list(self.Members.keys())[-1]
                if deck == True:
                    self.add_member((_last_mem_no+1), self.Nodes[j * self.discr + 2 + k].Name, self.Nodes[j * self.discr + _pp + 2 + k].Name, 
                                        E, G, Iy, Iz, J, A, 
                                        auxNode=None,
                                        tension_only=False, 
                                        comp_only=False)
                else:
                    self.add_member((_last_mem_no+1), self.Nodes[j * self.discr + 1].Name, self.Nodes[j * self.discr + _pp + 1].Name, 
                                        E, G, Iy, Iz, J, A, 
                                        auxNode=None,
                                        tension_only=False, 
                                        comp_only=False)

            #for k in range(_sec_loop):
                for i in range(self.tr_discr-2):
                    if deck == True:
                        if i == 0:
                            _last_mem_no = list(self.Members.keys())[-1]
                        self.add_member((i+_last_mem_no+1), 
                                        self.Nodes[j * self.discr + (_number + 1) * i + _pp + 2 + k].Name, 
                                        self.Nodes[j * self.discr + (_number + 1) * i + _pp + _number + 3 + k].Name, 
                                        E, G, Iy, Iz, J, A, 
                                        auxNode=None,
                                        tension_only=False, 
                                        comp_only=False)
                    else:
                        self.add_member((i+_last_mem_no+2), 
                                        self.Nodes[j * self.discr + (_number + 1) * i + _pp + 1].Name, 
                                        self.Nodes[j * self.discr + (_number + 1) * i + _pp + _number + 2].Name, 
                                        E, G, Iy, Iz, J, A, 
                                        auxNode=None,
                                        tension_only=False, 
                                        comp_only=False)


                _last_mem_no = list(self.Members.keys())[-1]
                _curr_node = self.Members[_last_mem_no].j_node.Name
                if deck == True:
                    self.add_member((_last_mem_no+1), _curr_node, self.Nodes[j * self.discr + _number + 3 + k].Name, 
                                E, G, Iy, Iz, J, A, 
                                auxNode=None,
                                tension_only=False, 
                                comp_only=False)
                else:
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
    wd185.add_deck_trans_can()

    print(wd185.add_cross_members_(deck=False))
    print(wd185.add_cross_members_(deck=True))
    
    # Define the supports
    
    wd185.def_support(1.0, *(6 * [True]))
    wd185.def_support(18.0, *(6 * [True]))
    # wd185.def_support(21.0, *(6 * [True]))
    # wd185.def_support(42.0, *(6 * [True]))

    # Add nodal loads
    wd185.add_node_load(16.0, 'FY', -400)
    
    # Analyze the model
    wd185.analyze(check_statics=True)
    
    # Render the deformed shape
    Visualization.render_model(wd185, annotation_size=0.2, deformed_shape=True, deformed_scale=200, render_loads=True)
    
if __name__ == '__main__':
    main()