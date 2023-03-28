import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QHBoxLayout,QVBoxLayout
from pyqtgraph.parametertree import Parameter, ParameterTree

def sync_parameters(param, changes):
    for param, change, data in changes:
        # Find the corresponding parameter in the other tree
        other_param = other_tree.param(param.name())
        
        # Update the value of the other parameter
        other_param.setValue(data)

# Define the parameters
params = [
    {"name": "Interpolation", "type": "group", "children": [
        {"name": "Method", "type": "list", "values": ["Linear", "Cubic", "Spline"]},
        {"name": "Smoothness", "type": "float", "value": 0.5, "step": 0.1},
    ]},
    {"name": "Filtering", "type": "group", "children": [
        {"name": "Filter Type", "type": "list", "values": ["Low-pass", "High-pass", "Band-pass"]},
        {"name": "Cutoff Frequency", "type": "float", "value": 1.0, "step": 0.1},
    ]},
]


interpolation_settings = [
    {"name": "Interpolation", "type": "group", "children": [
        {"name": "Method", "type": "list", "values": ["Linear", "Cubic", "Spline"]},
    ]}
]

filter_settings = [
        {"name": "Filtering", "type": "group", "children": [
        {"name": "Filter Type", "type": "list", "values": ["Butterworth Low Pass"]},
        {"name": "Order", "type":"int","value":4, "step":.1},
        {"name": "Cutoff Frequency", "type": "float", "value": 6.0, "step": 0.1},
    ]}
]

interpolation_params = Parameter.create(name='interp_params', type='group', children=interpolation_settings)
filter_params = Parameter.create(name='filter_params',type='group', children=filter_settings )

# Create the Parameter Tree and set the parameters
app = QApplication([])
# tree = ParameterTree()
# tree.setParameters(Parameter.create(name='params', type='group', children=params), showTop=False)

tree1 = ParameterTree()
tree1.addParameters(interpolation_params, showTop=False)
tree1.addParameters(filter_params,showTop=False)

# Create the second Parameter Tree and set the parameters
# tree2 = ParameterTree()
# tree2.setParameters(param_test, showTop=False)

# # Set the second tree as the "other_tree" variable
# other_tree = tree2

# # Connect the "sigValueChanged" signal of the first tree to the "sync_parameters" function
# param_test.sigTreeStateChanged.connect(sync_parameters)
tree1.show()
# tree2.show()

# Show the tree widget
#tree.show()
app.exec()