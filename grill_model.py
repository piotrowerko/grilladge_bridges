import numpy as np
from PyNite.FEModel3D import FEModel3D
from grillage import Grillage
from PyNite import Visualization

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

class GrillModel(FEModel3D):
    """Instance of this class is a Grillage FE model,
    build on basis of instance of Grillage class instance from grillage module"""
    def __init__(self,
                 name, 
                 no_of_beams=2, 
                 beam_spacing=8, 
                 span_data=(2, 30, 30),
                 canti_l=2.5,
                 skew=60,
                 discr=10,
                 tr_discr=3,
                 onlybeam=False):
        #  https://www.youtube.com/watch?v=MBbVq_FIYDA
        super().__init__()
        self.name = name
        self.grillage = Grillage(no_of_beams, 
                                   beam_spacing, 
                                   span_data,
                                   canti_l,
                                   skew,
                                   onlybeam)
        self.grill_coors = self.grillage.grillage_nodes_c(discr, 
                                                         tr_discr)
        self.discr = discr
        self.tr_discr = tr_discr
        self.no_of_beams = no_of_beams

    def __str__(self):
        return f'{self.name}'
    
    def add_nodes(self, no_to_disp=1.0, onlybeam=False):
        node_data = self.grillage.add_name(self.grill_coors)
        __list = [i for i in range(len(node_data))]
        for el in node_data[__list]:
            self.add_node(*el)
        #return self.Nodes[no_to_disp].Name, self.Nodes[no_to_disp].X, self.Nodes[no_to_disp].Y, self.Nodes[no_to_disp].Z
        return node_data, list(self.Nodes[no_to_disp])  # this will only run when Node 3D class in pynite is changed
        #return type(self.Nodes)
    #  Unpacking Dictionaries With the ** Operator
    # https://stackabuse.com/unpacking-in-python-beyond-parallel-assignment/
    
    def add_girders(self, E=35000000, G=16000000, 
                Iy=1, Iz=1, J=1, A=1, auxNode=None,
                tension_only=False, comp_only=False):
        """adds FE members representing bridge main deck girders"""
        _number_tot = int(self.discr * self.grillage.span_data[0] * self.no_of_beams)
        _number = int(self.discr * self.grillage.span_data[0])
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
        """adds FE members representing bridge cantilevers in trans. direction"""
        if self.no_of_beams == 1:
            return self.Members
        _jj = int(self.discr * self.grillage.span_data[0] * self.no_of_beams + self.no_of_beams)  # _no_of_main_gird_fe + no_of_beams 
        _number = int(self.discr * self.grillage.span_data[0] + 1) # no of cantilevel FE on one side + 1
        _kk = (self.no_of_beams - 1) * (_number) + 1  # number of first node in last girder
        for i in range(0, _number, 1):
            # adding cantilevel FE - bottom egde:
            self.add_member((_jj+i-1), self.Nodes[(i+1)*1.0].Name, 
                            self.Nodes[((_jj+i+1)*1.0)].Name, 
                            E, G, Iy, Iz, J, A, 
                            auxNode=None,
                            tension_only=False, 
                            comp_only=False)
            # adding cantilevel FE - upper egde:
            self.add_member((_jj-1+_number+i), self.Nodes[(_kk+i)*1.0].Name, 
                            self.Nodes[((_jj+_number+1+i)*1.0)].Name, 
                            E, G, Iy, Iz, J, A, 
                            auxNode=None,
                            tension_only=False, 
                            comp_only=False)
        return self.Members


    def add_cross_members_(self, E=35000000, G=16000000, 
                Iy=1, Iz=1, J=1, A=1, auxNode=None,
                tension_only=False, comp_only=False, deck=False):
        """adds FE members representing cross members or bridge deck in trans. dir."""
        if self.no_of_beams == 1:
            return self.Members
        _number_tot = int(self.discr * self.grillage.span_data[0] * self.no_of_beams)
        _number = int(self.discr * self.grillage.span_data[0])
        _pp = _number_tot + self.no_of_beams + 2 * _number + 2  # number of nodes in longitudinal members + cantiENDs nodes
        
        # adding _loop variables for creation of additional trans. bars repr. deck in trans. dir.:
        if deck == True:
            _first_loop = self.grillage.span_data[0]  # eq. to number of spans
            _sec_loop = int(self.discr) - 1  # eq. to number of cross lines of deck cross bars in each span
        else:
            _first_loop = self.grillage.span_data[0] + 1  # eq. to number of support cross members
            _sec_loop = 1
        
        for j in range(_first_loop):
            for k in range(_sec_loop):
                _last_mem_no = list(self.Members.keys())[-1]
                if deck == True:
                    self.add_member((_last_mem_no+1), self.Nodes[j * self.discr + 2 + k].Name, 
                                        self.Nodes[j * self.discr + _pp + 2 + k].Name, 
                                        E, G, Iy, Iz, J, A, 
                                        auxNode=None,
                                        tension_only=False, 
                                        comp_only=False)
                else:
                    self.add_member((_last_mem_no+1), self.Nodes[j * self.discr + 1].Name, 
                                        self.Nodes[j * self.discr + _pp + 1].Name, 
                                        E, G, Iy, Iz, J, A, 
                                        auxNode=None,
                                        tension_only=False, 
                                        comp_only=False)

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
                    self.add_member((_last_mem_no+1), _curr_node, 
                                    self.Nodes[j * self.discr + _number + 3 + k].Name, 
                                E, G, Iy, Iz, J, A, 
                                auxNode=None,
                                tension_only=False, 
                                comp_only=False)
                else:
                    self.add_member((_last_mem_no+1), _curr_node, 
                                    self.Nodes[j * self.discr + _number + 2].Name, 
                                E, G, Iy, Iz, J, A, 
                                auxNode=None,
                                tension_only=False, 
                                comp_only=False)
        return _last_mem_no, _pp

    def add_cross_members_new_(self, E=35000000, G=16000000, 
                Iy=1, Iz=1, J=1, A=1, auxNode=None,
                tension_only=False, comp_only=False, deck=False):
        """adds FE members representing cross members or bridge deck in trans. dir."""
        if self.no_of_beams == 1:
            return self.Members
        _number_tot = int(self.discr * self.grillage.span_data[0] * self.no_of_beams)
        _number = int(self.discr * self.grillage.span_data[0])
        _pp = _number_tot + self.no_of_beams + 2 * _number + 2  # number of nodes in longitudinal members + cantiENDs nodes
        _qq = (_number + 1) * (self.tr_discr - 1)# liczba węzłów wewnętrznych pomiędzy belkami
        
        # adding _loop variables for creation of additional trans. bars repr. deck in trans. dir.:
        if deck == True:
            _first_loop = self.grillage.span_data[0]  # eq. to number of spans
            _sec_loop = int(self.discr) - 1  # eq. to number of cross lines of deck cross bars in each span
        else:
            _first_loop = self.grillage.span_data[0] + 1  # eq. to number of support cross members
            _sec_loop = 1
        
        for a in range(0, self.no_of_beams - 1, 1):
            for j in range(_first_loop):
                for k in range(_sec_loop):
                    _last_mem_no = list(self.Members.keys())[-1]
                    if deck == True:
                        self.add_member((_last_mem_no+1), self.Nodes[a * (_number + 1) + j * self.discr + 2 + k].Name, 
                                            self.Nodes[a * _qq + j * self.discr + _pp + 2 + k].Name, 
                                            E, G, Iy, Iz, J, A, 
                                            auxNode=None,
                                            tension_only=False, 
                                            comp_only=False)
                    else:
                        self.add_member((_last_mem_no+1), self.Nodes[a * (_number + 1) + j * self.discr + 1].Name, 
                                            self.Nodes[a * _qq + j * self.discr + _pp + 1].Name, 
                                            E, G, Iy, Iz, J, A, 
                                            auxNode=None,
                                            tension_only=False, 
                                            comp_only=False)

                    for i in range(self.tr_discr-2):
                        if deck == True:
                            if i == 0:
                                _last_mem_no = list(self.Members.keys())[-1]
                            self.add_member((i+_last_mem_no+1), 
                                            self.Nodes[a * _qq + j * self.discr + (_number + 1) * i + _pp + 2 + k].Name, 
                                            self.Nodes[a * _qq + j * self.discr + (_number + 1) * i + _pp + _number + 3 + k].Name, 
                                            E, G, Iy, Iz, J, A, 
                                            auxNode=None,
                                            tension_only=False, 
                                            comp_only=False)
                        else:
                            self.add_member((i+_last_mem_no+2), 
                                            self.Nodes[a * _qq + j * self.discr + (_number + 1) * i + _pp + 1].Name, 
                                            self.Nodes[a * _qq + j * self.discr + (_number + 1) * i + _pp + _number + 2].Name, 
                                            E, G, Iy, Iz, J, A, 
                                            auxNode=None,
                                            tension_only=False, 
                                            comp_only=False)


                    _last_mem_no = list(self.Members.keys())[-1]
                    _curr_node = self.Members[_last_mem_no].j_node.Name
                    if deck == True:
                        self.add_member((_last_mem_no+1), _curr_node, 
                                        self.Nodes[a * (_number + 1) + j * self.discr + _number + 3 + k].Name, 
                                    E, G, Iy, Iz, J, A, 
                                    auxNode=None,
                                    tension_only=False, 
                                    comp_only=False)
                    else:
                        self.add_member((_last_mem_no+1), _curr_node, 
                                        self.Nodes[a * (_number + 1) + j * self.discr + _number + 2].Name, 
                                    E, G, Iy, Iz, J, A, 
                                    auxNode=None,
                                    tension_only=False, 
                                    comp_only=False)
        return _last_mem_no, _pp

    def add_gird_suppports(self):
        """adds node supports at intersections of girder and support axes"""
        int(self.discr) #* self.grillage.span_data[0])
        #'1 3 5 6 8 10'
        # compute number of intersections:
        num_of_in = self.no_of_beams * (self.grillage.span_data[0] + 1)
        sup_node_number = 1.0
        j = 0
        for i in range(num_of_in):
            self.def_support(sup_node_number, 
                             *(3 * [True]), 
                             *(3 * [False]))
            if (j) < self.grillage.span_data[0]:
                sup_node_number += self.discr
                j += 1
            else:
                sup_node_number += 1
                j = 0
    
    def load_with_unit_load(self, node):
        "adds loads and results from node unit loads"
        node_disp_vert = np.array([])
        for key in self.Nodes.keys():
            if key == None:
                pass
            else:
                self.add_node_load(key, 'FY', -1000)
                self.analyze(check_statics=False)
                node_disp_vert = np.append(node_disp_vert, [self.Nodes[key].DY['Combo 1']])
        return node_disp_vert

    def _load_with_unit_load(self):
        "adds unit loads and and creates factors dictionary"
        _factors = {}
        for key in self.Nodes.keys():
            if key == None:
                pass
            else:
                self.add_node_load(key, 'FY', -1000, case=key)
                # creating dictionary with load factors
                _factors[key] = 1.0
        return _factors
                
    
    def create_influence_data(self, node=None, member=None):
        "computes data for influence map in given node or member"
            
        if node or member:
            _factors = self._load_with_unit_load()
            for key in self.Nodes.keys():
                if key == None:
                    pass
                else:
                    self.add_load_combo(key, factors={key:1.0})  # creates numerous load combos, each with only one factor = 1.0
                    # number of compos is equal to number of nodes
            self.analyze(check_statics=False)
            #node_disp_vert = np.append(node_disp_vert, [self.Nodes[key].DY['inf_data']])
        else: pass
        if node and member == None:
            node_disp_vert = {}
            for key in self.Nodes.keys():
                if key == None:
                    pass
                else:
                    node_disp_vert[key] = self.Nodes[node].DY[key]
            return node_disp_vert
        elif member and node == None:
            memb_bend_moment = {}
            for key in self.Nodes.keys():
                if key == None:
                    pass
                else:
                    memb_bend_moment[key] = self.Members[member].moment('Mz', 0.01, key)
            return memb_bend_moment
        else: pass
    
    def gen_np_data_for_plot(self, node_data, analysed_data):
        """returns np array of influence 3d function discrete representation
        for visaulisations"""
        _infl_data = node_data
        _vals = np.array([val for val in analysed_data.values()])
        v_vals = np.vstack(_vals)
        infl_data = np.append(_infl_data, v_vals, axis=1)
        return infl_data

    def print_3d_plot(self, data):
        """plots influence scatter plot of given data"""
        longi_cor = data[:, 3]  # "z" in pynite; "x" in arsap
        trans_cor = data[:, 1]  # "x" in pynite; "y" in arsap
        infl_data = data[:, 4]
        name_data = data[:, 0]
        fig = plt.figure()
        #ax = fig.gca(projection='3d')
        ax = fig.add_subplot(111, projection='3d')
        # X = np.arange(0, iy, 1)
        # Y = np.arange(0, ix, 1)
        #longi_cor, trans_cor = np.meshgrid(longi_cor, trans_cor)

        #surf = ax.plot_surface(longi_cor, trans_cor, infl_data, cmap=cm.coolwarm,
        #                       linewidth=0, antialiased=False)
        # Customize the z axis.
        # ax.set_zlim(4, 12)
        # ax.zaxis.set_major_locator(LinearLocator(10))
        # ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
        #ax.scatter(longi_cor, trans_cor, infl_data, c='y', marker='o')
        surf = ax.plot_trisurf(longi_cor, trans_cor, infl_data, cmap=cm.jet, linewidth=0)
        fig.colorbar(surf)
        ax.view_init(30, 20)
        plt.show()

# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
# from matplotlib import cm
# from matplotlib.ticker import LinearLocator, FormatStrFormatter
# import numpy as np


# fig = plt.figure()
# ax = fig.gca(projection='3d')
# X = np.arange(0, iy, 1)
# Y = np.arange(0, ix, 1)
# X, Y = np.meshgrid(X, Y)

# Z=P
# surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
#                        linewidth=0, antialiased=False)
# # Customize the z axis.
# ax.set_zlim(4, 12)
# ax.zaxis.set_major_locator(LinearLocator(10))
# ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
# ax.view_init(75, 20)
# plt.show()

# # Add nodal loads
# frame.add_node_load('N2', 'FY', -400, case=1.0)
# frame.add_node_load('N5', 'FY', -400, case=1.0)

# frame.add_load_combo('ppp', factors={1.0:1.0})

# # Analyze the model
# frame.analyze(check_statics=True)

# # Render the deformed shape
# Visualization.render_model(frame, deformed_shape=True, deformed_scale=200, render_loads=True, combo_name='ppp')

def main():
    wd185 = GrillModel('wd_185')

    node_data = wd185.add_nodes()[0]
    wd185.add_girders()
    wd185.add_deck_trans_can()

    wd185.add_cross_members_new_(deck=False)
    wd185.add_cross_members_new_(deck=True)
    
    # # Define the supports
    # wd185.def_support(42.0, *(6 * [True]))
    wd185.add_gird_suppports()

    # Add nodal loads
    #wd185.add_node_load(2.0, 'FY', -400)
    
    # Analyze the model
    #wd185.analyze(check_statics=True)
    
    # Render the deformed shape
    Visualization.render_model(wd185, annotation_size=0.2, deformed_shape=False, deformed_scale=200, render_loads=False)
    
    # print('N1 displacement in Y =', wd185.Nodes[2.0].DY)
    
    # print(wd185.Nodes[1.0].Name)
    
    member = 6.0
    #wd185._load_with_unit_load(node)
    comp_data = wd185.create_influence_data(member=member)  # choosing Mz influence map
    # one can choose node=node and to create the displacement influence map
    data = wd185.gen_np_data_for_plot(node_data, comp_data)
    wd185.print_3d_plot(data)

if __name__ == '__main__':
    main()