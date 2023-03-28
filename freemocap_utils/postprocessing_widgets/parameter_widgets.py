from pyqtgraph.parametertree import Parameter, ParameterTree

interpolation_settings = [
    {"name": "Interpolation", "type": "group", "children": [
        {"name": "Method", "type": "list", "values": ["linear", "cubic", "spline"]},
    ]}
]

filter_settings = [
        {"name": "Filtering", "type": "group", "children": [
        {"name": "Filter Type", "type": "list", "values": ["Butterworth Low Pass"]},
        {"name": "Order", "type":"int","value":4, "step":.1},
        {"name": "Cutoff Frequency", "type": "float", "value": 6.0, "step": 0.1},
        {"name": "Sampling Rate", "type": "float", "value": 30.0, "step": 0.1},
    ]}
]

interpolation_params = Parameter.create(name='interp_params', type='group', children=interpolation_settings)
filter_params = Parameter.create(name='filter_params',type='group', children=filter_settings )

def get_interpolation_parameter(interpolation_settings):
    interpolation_params = Parameter.create(name='interp_params', type='group', children=interpolation_settings)
    return interpolation_params

def get_filter_parameter(filter_settings):
    filter_params = Parameter.create(name='filter_params',type='group', children=filter_settings )
    return filter_params
