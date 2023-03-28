from pathlib import Path
import numpy as np

from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QHBoxLayout,QVBoxLayout, QPushButton
from freemocap_utils.postprocessing_widgets.slider_widget import FrameCountSlider
from freemocap_utils.postprocessing_widgets.skeleton_view_widget import SkeletonViewWidget

from freemocap_utils.postprocessing_widgets.parameter_widgets import interpolation_params, filter_params
from freemocap_utils.postprocessing_widgets.postprocessing_functions.interpolate_data import interpolate_skeleton_data
from freemocap_utils.postprocessing_widgets.postprocessing_functions.filter_data import filter_skeleton_data

from pyqtgraph.parametertree import ParameterTree

class MainWindow(QMainWindow):
    def __init__(self,freemocap_raw_data:np.ndarray):
        super().__init__()

        layout = QVBoxLayout()
        widget = QWidget()

        num_frames = freemocap_raw_data.shape[0]
        self.frame_count_slider = FrameCountSlider(num_frames)
        layout.addWidget(self.frame_count_slider)

        viewer_layout = QHBoxLayout()

        self.raw_skeleton_viewer = SkeletonViewWidget()
        viewer_layout.addWidget(self.raw_skeleton_viewer)
        self.processed_skeleton_viewer = SkeletonViewWidget()
        viewer_layout.addWidget(self.processed_skeleton_viewer)
        layout.addLayout(viewer_layout)

        main_tree = self.create_main_page_parameter_tree()
        layout.addWidget(main_tree)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.connect_signals_to_slots()

        self.raw_skeleton_viewer.load_skeleton(freemocap_raw_data)

        self.process_button = QPushButton('Process Data')
        self.process_button.clicked.connect(self.postprocess_data)
        layout.addWidget(self.process_button)

        #self.postprocess_data()

    def connect_signals_to_slots(self):
        self.frame_count_slider.slider.valueChanged.connect(self.update_viewer_plots)

    def create_main_page_parameter_tree(self):
        main_tree = ParameterTree()
        main_tree.addParameters(interpolation_params, showTop=False)
        main_tree.addParameters(filter_params,showTop=False)

        return main_tree

    
    def update_viewer_plots(self):
        self.raw_skeleton_viewer.replot(self.frame_count_slider.slider.value())

        if self.processed_skeleton_viewer.skeleton_loaded:
            self.processed_skeleton_viewer.replot(self.frame_count_slider.slider.value())

    def get_all_parameter_values(self,parameter_object):
        values = {}
        for child in parameter_object.children(): #using this just to access the second level of the parameter tree
            if child.hasChildren():
                for grandchild in child.children():
                    values[grandchild.name()] = grandchild.value()
            else:
                values[child.name()] = child.value()
        return values
        


    def postprocess_data(self):
        interpolation_values_dict = self.get_all_parameter_values(interpolation_params)
        interpolated_skeleton = interpolate_skeleton_data(freemocap_raw_data,method_to_use= interpolation_values_dict['Method'])

        filter_values_dict = self.get_all_parameter_values(filter_params)
        filtered_skeleton = filter_skeleton_data(interpolated_skeleton, order = filter_values_dict['Order'], cutoff= filter_values_dict['Cutoff Frequency'], sampling_rate= filter_values_dict['Sampling Rate'])

        self.processed_skeleton_viewer.load_skeleton(filtered_skeleton)
        f = 2
             

if __name__ == "__main__":
    
    path_to_freemocap_session_folder = Path(r'D:\ValidationStudy2022\FreeMocap_Data\sesh_2022-05-24_16_10_46_JSM_T1_WalkRun')
    freemocap_raw_data = np.load(path_to_freemocap_session_folder/'DataArrays'/'mediaPipeSkel_3d.npy')

    app = QApplication([])
    win = MainWindow(freemocap_raw_data)

    win.show()
    app.exec()
