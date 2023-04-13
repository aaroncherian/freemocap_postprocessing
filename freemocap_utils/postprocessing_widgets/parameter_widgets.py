from pyqtgraph.parametertree import Parameter,registerParameterType
from PyQt6.QtWidgets import QWidget, QHBoxLayout,QVBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox



interpolation_settings = [
    {"name": "Interpolation", "type": "group", "children": [
        {
        "name": "Method", 
         "type": "list", 
         "values": ["linear", "cubic", "spline"]
         },
        {
        "name": "Order (only used in spline interpolation)", 
         "type": "int", 
         "value":3, 
         "step":1
         }
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

# def get_interpolation_parameter(interpolation_settings):
#     interpolation_params = Parameter.create(name='interp_params', type='group', children=interpolation_settings)
#     return interpolation_params

# def get_filter_parameter(filter_settings):
#     filter_params = Parameter.create(name='filter_params',type='group', children=filter_settings )
#     return filter_params



class CustomGoodFrameParam(Parameter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_find_good_frame_param = self.child("Good Frame Finder").child('Auto-find Good Frame')
        self.good_frame_param = self.child("Good Frame Finder").child("Good Frame")

        self.auto_find_good_frame_param.sigValueChanged.connect(self.auto_find_good_frame_changed)
        # self.good_frame_param.setOpts(readonly=True)

    def auto_find_good_frame_changed(self, value):
        if value.value():
            self.good_frame_param.setValue("")
            self.good_frame_param.setOpts(readonly=True)

        else:
            if not self.good_frame_param.value():
                self.good_frame_param.setValue("0")
            self.good_frame_param.setOpts(readonly=False)



registerParameterType('CustomGoodFrameParam',CustomGoodFrameParam)
good_frame_finder_settings = [
    {"name": "Good Frame Finder", "type": "group", "children": [
        {"name": "Instructions", "type": "str", "value": "Uncheck 'Auto-find Good Frame' to type in the good frame manually.", "readonly": True},
        {"name": "Auto-find Good Frame", "type": "bool", "value": True},
        {"name": "Good Frame", "type": "str", "value": "", "step": 1},
    ]}
]
good_frame_finder_params = Parameter.create(name='good_frame_finder_params', type='CustomGoodFrameParam', children=good_frame_finder_settings)


# class RotationParameter(Parameter):
#     def __init__(self, **opts):
#         super(RotationParameter, self).__init__(**opts)
#         self.addChild({'name': 'Rotate Data:', 'type': 'bool', 'value': True})

#     def value(self):
#         child_param = self.child('Rotate Data:')
#         return child_param.value()


rotating_settings = [
    {"name": "Rotating", "type": "group", "children": [
        {"name": "Rotate Data:", "type": "bool", "value": True},
    ]}
]

rotating_params = Parameter.create(name='rotating_params', type='group', children=rotating_settings)

# good_frame_finder_settings = [
#     {
#         "name": "Good Frame Finder",
#         "type": "group",
#         "children": [
#             {"name": "Good Frame", "type": "int", "value": 0},
#             {"name": "Auto-Find Good Frame", "type": "bool", "value":True},
#         ],
#     }
# ]

# good_frame_finder_params = Parameter.create(
#     name="good_frame_finder_params", type="group", children=good_frame_finder_settings
# )

#good_frame_finder_params.child("Good Frame Finder").child('Good Frame').value()

if __name__ == "__main__":

    def get_all_parameter_values(parameter_object):
        values = {}
        for child in parameter_object.children(): #using this just to access the second level of the parameter tree
            if child.hasChildren():
                for grandchild in child.children():
                    values[grandchild.name()] = grandchild.value()
            else:
                values[child.name()] = child.value()
        return values

    values = get_all_parameter_values(good_frame_finder_params)
    f =2 