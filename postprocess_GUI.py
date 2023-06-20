from pathlib import Path
import numpy as np

from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QHBoxLayout,QVBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox
from PyQt6.QtGui import QIntValidator

from freemocap_utils.postprocessing_widgets.slider_widget import FrameCountSlider
from freemocap_utils.postprocessing_widgets.task_worker_thread import TaskWorkerThread
from freemocap_utils.postprocessing_widgets.skeleton_viewers_container import SkeletonViewersContainer
from freemocap_utils.postprocessing_widgets.led_widgets import LedContainer
from freemocap_utils.postprocessing_widgets.parameter_tree_builder import create_main_page_parameter_tree
from freemocap_utils.postprocessing_widgets.parameter_widgets import rotating_params





import time



class MainWindow(QMainWindow):
    def __init__(self,freemocap_raw_data:np.ndarray):
        super().__init__()
        self.task_list = ['interpolating', 'filtering', 'finding good frame', 'rotating skeleton', 'plotting']
        layout = QVBoxLayout()
        widget = QWidget()
        
        self.freemocap_raw_data = freemocap_raw_data
        num_frames = freemocap_raw_data.shape[0]
        self.frame_count_slider = FrameCountSlider(num_frames)
        layout.addWidget(self.frame_count_slider)

        self.led_container = LedContainer(self.task_list)
        self.progress_led_dict, led_layout = self.led_container.create_led_indicators()
        layout.addLayout(led_layout)

        self.skeleton_viewers_container = SkeletonViewersContainer()
        layout.addWidget(self.skeleton_viewers_container)

        self.main_tree = create_main_page_parameter_tree()
        layout.addWidget(self.main_tree)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.connect_signals_to_slots()

        self.skeleton_viewers_container.plot_raw_skeleton(self.freemocap_raw_data)

        self.process_button = QPushButton('Process Data')
        self.process_button.clicked.connect(self.postprocess_data)
        layout.addWidget(self.process_button)

    def connect_signals_to_slots(self):
        self.frame_count_slider.slider.valueChanged.connect(lambda: self.update_viewer_plots(self.frame_count_slider.slider.value()))
        
    def update_viewer_plots(self, frame_to_plot):
        self.skeleton_viewers_container.update_raw_viewer_plot(frame_to_plot)
        self.skeleton_viewers_container.update_processed_viewer_plot(frame_to_plot)
        
    def postprocess_data(self):
        self.led_container.change_leds_to_tasks_not_started_color()

        self.worker_thread = TaskWorkerThread(raw_skeleton_data=self.freemocap_raw_data, task_list=self.task_list)
        self.worker_thread.start()
        self.worker_thread.task_running_signal.connect(self.handle_task_started)
        self.worker_thread.task_completed_signal.connect(self.handle_task_completed)
        self.worker_thread.all_tasks_finished_signal.connect(self.handle_plotting)

    def handle_task_started(self,task):
        self.led_container.change_led_to_task_is_running_color(task)

    def handle_task_completed(self,task):

        self.led_container.change_led_to_task_is_finished_color(task)

    def handle_plotting(self,task_results:dict):
        good_frame = task_results['finding good frame']['result']
        self.interpolated_skeleton = task_results['interpolating']['result']
        self.filtered_skeleton = task_results['filtering']['result']
        self.rotated_skeleton = task_results['rotating skeleton']['result']

        if self.rotated_skeleton is not None:
            self.skeleton_viewers_container.plot_processed_skeleton(self.rotated_skeleton)
        else:
            self.skeleton_viewers_container.plot_processed_skeleton(self.filtered_skeleton)
        
        self.update_viewer_plots(good_frame)
        self.frame_count_slider.slider.setValue(good_frame)

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


if __name__ == "__main__":
    
    #path_to_freemocap_session_folder = Path(r'D:\ValidationStudy2022\FreeMocap_Data\sesh_2022-05-24_16_10_46_JSM_T1_WalkRun')
    #path_to_freemocap_session_folder = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\recording_15_20_51_gmt-4__brit_half_inch')
    #path_to_freemocap_session_folder = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\recording_15_22_56_gmt-4__brit_one_inch')
    path_to_freemocap_session_folder = Path(r'D:\2023-05-10_session_aaron_michael_jon_milo\1.0_recordings\calibration_one\sesh_2023-05-10_16_24_38_body_calibration')
    freemocap_raw_data = np.load(path_to_freemocap_session_folder/'output_data'/'raw_data'/'mediapipe3dData_numFrames_numTrackedPoints_spatialXYZ.npy')

    freemocap_raw_data = freemocap_raw_data[:,0:33,:]

    app = QApplication([])
    win = MainWindow(freemocap_raw_data)

    win.show()
    app.exec()
