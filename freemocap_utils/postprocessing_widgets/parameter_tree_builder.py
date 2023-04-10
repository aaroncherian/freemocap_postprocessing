
from pyqtgraph.parametertree import ParameterTree

from freemocap_utils.postprocessing_widgets.parameter_widgets import interpolation_params, filter_params, rotating_params, good_frame_finder_params




def create_main_page_parameter_tree():
    main_tree = ParameterTree()
    main_tree.addParameters(interpolation_params, showTop=False)
    main_tree.addParameters(filter_params, showTop=False)
    main_tree.addParameters(good_frame_finder_params,showTop = False)
    main_tree.addParameters(rotating_params, showTop=False)

    return main_tree

def create_interpolation_parameter_tree():
    interpolation_tree = ParameterTree()
    interpolation_tree.addParameters(interpolation_params)

    return interpolation_tree

def create_filter_parameter_tree():
    filter_tree = ParameterTree()
    filter_tree.addParameters(filter_params)

    return filter_tree
