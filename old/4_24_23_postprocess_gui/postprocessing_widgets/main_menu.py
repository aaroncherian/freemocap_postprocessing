

import numpy as np

from PyQt6.QtWidgets import QWidget,QVBoxLayout, QPushButton,QGroupBox, QHBoxLayout, QLineEdit, QLabel

from PyQt6.QtCore import pyqtSignal

from freemocap_utils.postprocessing_widgets.slider_widget import FrameCountSlider
from freemocap_utils.postprocessing_widgets.task_worker_thread import TaskWorkerThread
from freemocap_utils.postprocessing_widgets.skeleton_viewers_container import SkeletonViewersContainer
from freemocap_utils.postprocessing_widgets.led_widgets import LedContainer
from freemocap_utils.postprocessing_widgets.parameter_tree_builder import create_main_page_parameter_tree, create_main_page_settings_dict
from freemocap_utils.postprocessing_widgets.stylesheet import groupbox_stylesheet, button_stylesheet


class MainMenu(QWidget):
    
    save_skeleton_data_signal = pyqtSignal(object,object,object)
    def __init__(self,freemocap_raw_data:np.ndarray):
        super().__init__()
        self.task_list = ['interpolation', 'filtering', 'finding good frame', 'skeleton rotation', 'results visualization', 'data saved']
        layout = QVBoxLayout()

        self.setStyleSheet(groupbox_stylesheet)
        
        self.freemocap_raw_data = freemocap_raw_data

        skeleton_viewer_groupbox = self.create_skeleton_viewer_groupbox()
        layout.addWidget(skeleton_viewer_groupbox)

        parameter_groupbox = self.create_parameter_groupbox()
        layout.addWidget(parameter_groupbox)

        self.connect_signals_to_slots()

        self.skeleton_viewers_container.plot_raw_skeleton(self.freemocap_raw_data)

        led_groupbox = self.create_led_groupbox()
        layout.addWidget(led_groupbox)

        save_groupbox = self.create_save_widgets()
        layout.addWidget(save_groupbox)

        self.setLayout(layout)

    def create_led_groupbox(self):
        groupbox = QGroupBox('Processing Progress')
        self.led_container = LedContainer(self.task_list)
        self.progress_led_dict, led_layout = self.led_container.create_led_indicators()
        groupbox.setLayout(led_layout)
        return groupbox
    
    def create_skeleton_viewer_groupbox(self):
        groupbox = QGroupBox('View your raw and processed mocap data')
        viewer_layout = QVBoxLayout()
        self.frame_count_slider = FrameCountSlider(num_frames= self.freemocap_raw_data.shape[0])
        viewer_layout.addWidget(self.frame_count_slider)
        self.skeleton_viewers_container = SkeletonViewersContainer()
        viewer_layout.addWidget(self.skeleton_viewers_container)
        groupbox.setLayout(viewer_layout)
        return groupbox
    
    def create_parameter_groupbox(self):
        groupbox = QGroupBox('Processing Parameters')
        parameter_layout = QVBoxLayout()
        self.main_tree = create_main_page_parameter_tree()
        parameter_layout.addWidget(self.main_tree)
        groupbox.setLayout(parameter_layout)
        return groupbox

    def create_save_widgets(self):

        groupbox = QGroupBox('Process and save out data')
        process_and_save_layout = QVBoxLayout()

        self.process_button = QPushButton('Process data and view results')
        self.process_button.clicked.connect(self.postprocess_data)
        self.process_button.setStyleSheet(button_stylesheet)
        process_and_save_layout.addWidget(self.process_button)

        save_layout = QHBoxLayout()

        save_label = QLabel('Name for saved file:')
        save_layout.addWidget(save_label)
        self.save_entry = QLineEdit()
        self.save_entry.setMaximumWidth(600)
        self.save_entry.setText('mediapipe_body_3d_xyz')
        save_layout.addWidget(self.save_entry)

        self.save_button = QPushButton('Save out data')
        self.save_button.setMinimumSize(300, 20)
        self.save_button.setStyleSheet(button_stylesheet)
        self.save_button.clicked.connect(self.save_skeleton_data)
        save_layout.addWidget(self.save_button)
        save_layout.addStretch(0)

        process_and_save_layout.addLayout(save_layout)
        groupbox.setLayout(process_and_save_layout)
        return groupbox

    def connect_signals_to_slots(self):
        self.frame_count_slider.slider.valueChanged.connect(lambda: self.update_viewer_plots(self.frame_count_slider.slider.value()))
        
    def update_viewer_plots(self, frame_to_plot):
        self.skeleton_viewers_container.update_raw_viewer_plot(frame_to_plot)
        self.skeleton_viewers_container.update_processed_viewer_plot(frame_to_plot)
        
    def postprocess_data(self):
        self.led_container.change_leds_to_tasks_not_started_color()
        self.settings_dict = create_main_page_settings_dict()
        self.worker_thread = TaskWorkerThread(
            raw_skeleton_data=self.freemocap_raw_data,
            task_list=self.task_list,
            settings=self.settings_dict,
            task_running_callback=self.handle_task_started,
            task_completed_callback=self.handle_task_completed,
            all_tasks_finished_callback=self.handle_plotting,
        )   
             
        self.worker_thread.start()


    def handle_task_started(self,task):
        self.led_container.change_led_to_task_is_running_color(task)

    def handle_task_completed(self,task,result=None):
        if result is None:
            self.led_container.change_led_to_task_not_started_color(task)
        else:
            self.led_container.change_led_to_task_is_finished_color(task)

    def save_skeleton_data(self):
        # file_path_to_save = 
        final_skeleton = self.get_final_processed_skeleton()
        skeleton_save_file_name = self.save_entry.text()
        self.save_skeleton_data_signal.emit(final_skeleton,skeleton_save_file_name,self.settings_dict)
        self.handle_task_completed('data saved', result = True)


    def get_final_processed_skeleton(self):
        if self.rotated_skeleton is not None:
            return self.rotated_skeleton
        elif self.filtered_skeleton is not None:
            return self.filtered_skeleton
        else:
            return self.interpolated_skeleton

    def handle_plotting(self,task_results:dict):
        good_frame = task_results['finding good frame']['result']
        self.interpolated_skeleton = task_results['interpolation']['result']
        self.filtered_skeleton = task_results['filtering']['result']
        self.rotated_skeleton = task_results['skeleton rotation']['result']

        if self.rotated_skeleton is not None:
            self.skeleton_viewers_container.plot_processed_skeleton(self.rotated_skeleton)
        else:
            self.skeleton_viewers_container.plot_processed_skeleton(self.filtered_skeleton)
        
        self.update_viewer_plots(good_frame)
        self.frame_count_slider.slider.setValue(good_frame)

        self.handle_task_completed('results visualization', result = True)
