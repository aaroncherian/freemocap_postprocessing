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

from freemocap_utils.postprocessing_widgets.led_widgets import LEDIndicator, LedContainer

import time

class MainWindow(QMainWindow):
    def __init__(self,freemocap_raw_data:np.ndarray):
        super().__init__()

        layout = QVBoxLayout()
        widget = QWidget()

        num_frames = freemocap_raw_data.shape[0]
        self.frame_count_slider = FrameCountSlider(num_frames)
        layout.addWidget(self.frame_count_slider)

        self.led_container = LedContainer()
        self.progress_led_dict, led_layout = self.led_container.create_led_indicators()
        layout.addLayout(led_layout)

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

        self.skeleton_viewers_container.plot_raw_skeleton(freemocap_raw_data)

        self.process_button = QPushButton('Process Data')
        self.process_button.clicked.connect(self.postprocess_data)
        layout.addWidget(self.process_button)

    def connect_signals_to_slots(self):
        self.frame_count_slider.slider.valueChanged.connect(self.update_viewer_plots)
        

    def create_main_page_parameter_tree(self):
        main_tree = ParameterTree()
        main_tree.addParameters(interpolation_params, showTop=False)
        main_tree.addParameters(filter_params,showTop=False)

        return main_tree

    def update_viewer_plots(self):
        self.skeleton_viewers_container.update_raw_viewer_plot(self.frame_count_slider.slider.value())
        self.skeleton_viewers_container.update_processed_viewer_plot(self.frame_count_slider.slider.value())
        
    def postprocess_data(self):
        self.led_container.change_leds_to_tasks_not_started_color()

        if self.good_frame_entry.good_frame_entry.text():
            self.good_frame = int(self.good_frame_entry.good_frame_entry.text())
        else:
            self.good_frame = None
            
        rotate_skeleton_bool = self.rotation_check.rotation_checkbox.isChecked()
        self.worker_thread = WorkerThread(good_frame = self.good_frame, run_rotate_skeletons=rotate_skeleton_bool)
        self.worker_thread.start()
        self.worker_thread.task_running_signal.connect(self.handle_task_started)
        self.worker_thread.task_completed_signal.connect(self.handle_task_completed)
        self.worker_thread.result_signal.connect(self.handle_plotting)

    def handle_task_started(self,task):
        self.led_container.change_led_to_task_is_running_color(task)

    def handle_task_completed(self,task,result=None):
        if task == 'finding good frame':
            self.good_frame_entry.good_frame_checkbox.setChecked(False)
            self.good_frame_entry.good_frame_entry.setText(str(result))
        self.led_container.change_led_to_task_is_finished_color(task)

    def handle_plotting(self,result):
        self.skeleton_viewers_container.plot_processed_skeleton(result)
        self.handle_task_completed('plotting')


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
    task_running_signal = pyqtSignal(str)
    task_completed_signal = pyqtSignal(str, object)
    result_signal = pyqtSignal(object) 
    def __init__(self, run_rotate_skeletons = True, good_frame = None):
        super().__init__()
        self.good_frame = good_frame
        self.run_rotate_skeletons = run_rotate_skeletons  

    def run(self):
        
        self.task_running_signal.emit('interpolating')
        interpolation_values_dict = self.get_all_parameter_values(interpolation_params)
        interpolated_skeleton = interpolate_skeleton_data(freemocap_raw_data,method_to_use= interpolation_values_dict['Method'])
        self.task_completed_signal.emit('interpolating', None)

        self.task_running_signal.emit('filtering')
        filter_values_dict = self.get_all_parameter_values(filter_params)
        filtered_skeleton = filter_skeleton_data(interpolated_skeleton, order = filter_values_dict['Order'], cutoff= filter_values_dict['Cutoff Frequency'], sampling_rate= filter_values_dict['Sampling Rate'])
        processed_skeleton= filtered_skeleton
        self.task_completed_signal.emit('filtering', None)

        if not self.good_frame:
            self.task_running_signal.emit('finding good frame')
            self.good_frame = find_good_frame(filtered_skeleton, skeleton_indices = mediapipe_indices, initial_velocity_guess=.5)
            
        self.task_completed_signal.emit('finding good frame', self.good_frame)

        if self.run_rotate_skeletons:
            self.task_running_signal.emit('rotating skeleton')
            origin_aligned_skeleton = align_skeleton_with_origin(filtered_skeleton,mediapipe_indices,self.good_frame)[0]
            processed_skeleton= origin_aligned_skeleton
            self.task_completed_signal.emit('rotating skeleton', None)
        
        
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
