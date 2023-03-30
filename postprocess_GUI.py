from pathlib import Path
import numpy as np

from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QHBoxLayout,QVBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIntValidator

from freemocap_utils.postprocessing_widgets.slider_widget import FrameCountSlider
from freemocap_utils.postprocessing_widgets.skeleton_view_widget import SkeletonViewWidget
from freemocap_utils.postprocessing_widgets.parameter_widgets import interpolation_params, filter_params
from freemocap_utils.postprocessing_widgets.postprocessing_functions.interpolate_data import interpolate_skeleton_data
from freemocap_utils.postprocessing_widgets.postprocessing_functions.filter_data import filter_skeleton_data
from freemocap_utils.postprocessing_widgets.postprocessing_functions.good_frame_finder import find_good_frame
from freemocap_utils.postprocessing_widgets.postprocessing_functions.rotate_skeleton import align_skeleton_with_origin

from freemocap_utils.postprocessing_widgets.skeleton_viewers_container import SkeletonViewersContainer

from freemocap_utils.mediapipe_skeleton_builder import mediapipe_indices

from pyqtgraph.parametertree import ParameterTree

from freemocap_utils.postprocessing_widgets.led_indicator_widget import LEDIndicator

import time

class MainWindow(QMainWindow):
    def __init__(self,freemocap_raw_data:np.ndarray):
        super().__init__()

        layout = QVBoxLayout()
        widget = QWidget()

        num_frames = freemocap_raw_data.shape[0]
        self.frame_count_slider = FrameCountSlider(num_frames)
        layout.addWidget(self.frame_count_slider)

        progress_led_name_list = ['interpolating', 'filtering', 'finding good frame', 'rotating skeleton', 'plotting']
        self.progress_led_dict, led_layout = self.create_led_indicators(progress_led_name_list)
        layout.addLayout(led_layout)

        # viewer_layout = QHBoxLayout()
        # self.raw_skeleton_viewer = SkeletonViewWidget()
        # viewer_layout.addWidget(self.raw_skeleton_viewer)
        # self.processed_skeleton_viewer = SkeletonViewWidget()
        # viewer_layout.addWidget(self.processed_skeleton_viewer)
        # layout.addLayout(viewer_layout)
        self.skeleton_viewers_container = SkeletonViewersContainer()
        layout.addWidget(self.skeleton_viewers_container)

        main_tree = self.create_main_page_parameter_tree()
        layout.addWidget(main_tree)

        self.good_frame_entry = GoodFrameWidget()
        layout.addWidget(self.good_frame_entry)

        self.rotation_check = RotationCheckBox()
        layout.addWidget(self.rotation_check)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.connect_signals_to_slots()

        # self.raw_skeleton_viewer.load_skeleton(freemocap_raw_data)
        self.skeleton_viewers_container.plot_raw_skeleton(freemocap_raw_data)

        self.process_button = QPushButton('Process Data')
        self.process_button.clicked.connect(self.postprocess_data)
        layout.addWidget(self.process_button)

    def connect_signals_to_slots(self):
        self.frame_count_slider.slider.valueChanged.connect(self.update_viewer_plots)
        
    def create_led_indicators(self, progress_led_name_list):
        progress_led_dict = {}

        led_layout = QHBoxLayout()

        for led_name in progress_led_name_list:
            led_indicator = LEDIndicator()
            progress_led_dict[led_name] = led_indicator

            led_label = QLabel(led_name.capitalize())

            led_item_layout = QHBoxLayout()
            led_item_layout.addWidget(led_indicator)
            led_item_layout.addWidget(led_label)

            led_layout.addLayout(led_item_layout)

        led_layout.addStretch()

        return progress_led_dict, led_layout

    def create_main_page_parameter_tree(self):
        main_tree = ParameterTree()
        main_tree.addParameters(interpolation_params, showTop=False)
        main_tree.addParameters(filter_params,showTop=False)

        return main_tree

    def update_viewer_plots(self):
        self.skeleton_viewers_container.update_raw_viewer_plot(self.frame_count_slider.slider.value())
        self.skeleton_viewers_container.update_processed_viewer_plot(self.frame_count_slider.slider.value())
        # self.skeleton_viewer_widget.update_raw_viewer_plot(self.frame_count_slider.slider.value())
        # self.skeleton_viewer_widget.update_processed_viewer_plot(self.frame_count_slider.slider.value())

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
        for led_indicator in self.progress_led_dict.values():
            led_indicator.set_unfinished_process_color()


        if self.good_frame_entry.good_frame_entry.text():
            self.good_frame = int(self.good_frame_entry.good_frame_entry.text())
        else:
            self.good_frame = None
            
        rotate_skeleton_bool = self.rotation_check.rotation_checkbox.isChecked()
        self.worker_thread = WorkerThread(good_frame = self.good_frame, run_rotate_skeletons=rotate_skeleton_bool)
        self.worker_thread.start()
        self.worker_thread.starting_signal.connect(self.update_process_starting_color)
        self.worker_thread.finished_signal.connect(self.update_process_finished_color)
        self.worker_thread.result_signal.connect(self.handle_plotting)


    def handle_plotting(self,result):
        self.skeleton_viewers_container.plot_processed_skeleton(result)
        # self.processed_skeleton_viewer.load_skeleton(result)
        self.update_process_finished_color('plotting')

    def update_process_starting_color(self,task):
        if task in self.progress_led_dict:
            self.progress_led_dict[task].set_in_process_color()

    def update_process_finished_color(self, task, result = None):
        if task in self.progress_led_dict:
            self.progress_led_dict[task].set_finished_process_color()

            if task == 'finding good frame':
                self.good_frame_entry.good_frame_checkbox.setChecked(False)
                self.good_frame_entry.good_frame_entry.setText(str(result))


class GoodFrameWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        self.good_frame_label = QLabel('Good Frame:')
        self.good_frame_entry = QLineEdit()
        self.good_frame_entry.setValidator(QIntValidator())
        self.good_frame_entry.setMaximumWidth(60)
        self.good_frame_checkbox = QCheckBox()
        self.checkbox_label = QLabel('Auto Find Good Frame')

        layout.addWidget(self.good_frame_label)
        layout.addWidget(self.good_frame_entry)
        layout.addWidget(self.good_frame_checkbox)
        layout.addWidget(self.checkbox_label)
        layout.addStretch()

        self.good_frame_checkbox.stateChanged.connect(self.checkbox_state_changed)

        self.good_frame_checkbox.setChecked(True)

        self.setLayout(layout)

    def checkbox_state_changed(self):
        if self.good_frame_checkbox.isChecked():
            self.good_frame_entry.setEnabled(False)
            self.good_frame_entry.setText(None)
        else:
            self.good_frame_entry.setEnabled(True)

    def get_input_value(self):
        if self.good_frame_entry.isEnabled():
            return int(self.good_frame_entry.text())
        else:
            return None
        
class RotationCheckBox(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.rotation_label = QLabel('Rotate Data:')
        self.rotation_checkbox = QCheckBox()

        layout.addWidget(self.rotation_label)
        layout.addWidget(self.rotation_checkbox)

        self.setLayout(layout)
        layout.addStretch()

        self.rotation_checkbox.setChecked(True)

    def get_checkbox_state(self):
        return self.rotation_checkbox.isChecked()        

class WorkerThread(QThread):
    starting_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, object)
    result_signal = pyqtSignal(object) 
    def __init__(self, run_rotate_skeletons = True, good_frame = None):
        super().__init__()
        self.good_frame = good_frame
        self.run_rotate_skeletons = run_rotate_skeletons  

    def run(self):
        
        self.starting_signal.emit('interpolating')
        interpolation_values_dict = self.get_all_parameter_values(interpolation_params)
        interpolated_skeleton = interpolate_skeleton_data(freemocap_raw_data,method_to_use= interpolation_values_dict['Method'])
        self.finished_signal.emit('interpolating', None)

        self.starting_signal.emit('filtering')
        filter_values_dict = self.get_all_parameter_values(filter_params)
        filtered_skeleton = filter_skeleton_data(interpolated_skeleton, order = filter_values_dict['Order'], cutoff= filter_values_dict['Cutoff Frequency'], sampling_rate= filter_values_dict['Sampling Rate'])
        processed_skeleton= filtered_skeleton
        self.finished_signal.emit('filtering', None)

        if not self.good_frame:
            self.starting_signal.emit('finding good frame')
            self.good_frame = find_good_frame(filtered_skeleton, skeleton_indices = mediapipe_indices, initial_velocity_guess=.5)
            
        self.finished_signal.emit('finding good frame', self.good_frame)

        if self.run_rotate_skeletons:
            self.starting_signal.emit('rotating skeleton')
            origin_aligned_skeleton = align_skeleton_with_origin(filtered_skeleton,mediapipe_indices,self.good_frame)[0]
            processed_skeleton= origin_aligned_skeleton
            self.finished_signal.emit('rotating skeleton', None)
        
        
        self.result_signal.emit(processed_skeleton)

    def get_all_parameter_values(self,parameter_object):
        values = {}
        for child in parameter_object.children(): #using this just to access the second level of the parameter tree
            if child.hasChildren():
                for grandchild in child.children():
                    values[grandchild.name()] = grandchild.value()
            else:
                values[child.name()] = child.value()
        return values

if __name__ == "__main__":
    
    path_to_freemocap_session_folder = Path(r'D:\ValidationStudy2022\FreeMocap_Data\sesh_2022-05-24_16_10_46_JSM_T1_WalkRun')
    freemocap_raw_data = np.load(path_to_freemocap_session_folder/'DataArrays'/'mediaPipeSkel_3d.npy')

    app = QApplication([])
    win = MainWindow(freemocap_raw_data)

    win.show()
    app.exec()
