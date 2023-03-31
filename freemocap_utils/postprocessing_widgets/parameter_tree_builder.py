
from pyqtgraph.parametertree import ParameterTree

from freemocap_utils.postprocessing_widgets.parameter_widgets import interpolation_params, filter_params

def create_main_page_parameter_tree():
    main_tree = ParameterTree()
    main_tree.addParameters(interpolation_params, showTop=False)
    main_tree.addParameters(filter_params, showTop=False)

    return main_tree