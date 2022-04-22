from PyNite import Visualization

from PyNite.FEModel3D import FEModel3D
from grillage import Grillage
from grill_model import GrillModel


def main():
    my_beam2d = GrillModel('moja belka 2d',
                            no_of_beams=1, 
                            beam_spacing=0, 
                            span_data=(1, 10.01),
                            canti_l=0,
                            skew=0,
                            discr=10,
                            tr_discr=0,
                            onlybeam=True)

    node_data = my_beam2d.add_nodes()[0]
    my_beam2d.add_girders()
    # my_beam2d.add_deck_trans_can()

    # my_beam2d.add_cross_members_new_(deck=False)
    # my_beam2d.add_cross_members_new_(deck=True)
    
    # # Define the supports
    # my_beam2d.def_support(42.0, *(6 * [True]))
    my_beam2d.add_gird_suppports()

    # Add nodal loads
    my_beam2d.add_node_load(6.0, 'FY', -1000)
    
    # Analyze the model
    my_beam2d.analyze(check_statics=True)
    
    # Render the deformed shape
    Visualization.render_model(my_beam2d, annotation_size=0.05, deformed_shape=True, deformed_scale=300, render_loads=True)

    # print('N1 displacement in Y =', my_beam2d.Nodes[2.0].DY)
    
    # print(my_beam2d.Nodes[1.0].Name)
    
    # node = 5.0

    # moment(self, Direction, x, combo_name='Combo 1')
    #MomentFrame.Members['Beam'].plot_moment('Mz', combo_name='1.2D+1.0W')
    print(my_beam2d.Members[5].moment('Mz', 0.01))
            
if __name__ == '__main__':
    main()