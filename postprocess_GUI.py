from pathlib import Path
import numpy as np

from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication,QVBoxLayout, QPushButton, QTabWidget,QGroupBox, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import pyqtSignal

from freemocap_utils.postprocessing_widgets.slider_widget import FrameCountSlider
from freemocap_utils.postprocessing_widgets.task_worker_thread import TaskWorkerThread
from freemocap_utils.postprocessing_widgets.skeleton_viewers_container import SkeletonViewersContainer
from freemocap_utils.postprocessing_widgets.led_widgets import LedContainer
from freemocap_utils.postprocessing_widgets.parameter_tree_builder import create_main_page_parameter_tree, create_interpolation_parameter_tree, create_filter_parameter_tree
from freemocap_utils.postprocessing_widgets.timeseries_view_widget import TimeSeriesPlotterWidget
from freemocap_utils.postprocessing_widgets.marker_selector_widget import MarkerSelectorWidget
from freemocap_utils.postprocessing_widgets.stylesheet import groupbox_stylesheet, button_stylesheet


class FileManager:
    def __init__(self, path_to_recording: str):
        self.path_to_recording = path_to_recording
        self.data_array_path = self.path_to_recording/'DataArrays'
    
    def load_skeleton_data(self):
        freemocap_raw_data = np.load(self.data_array_path/'mediaPipeSkel_3d.npy')
        freemocap_raw_data = freemocap_raw_data[:,0:33,:]
        return freemocap_raw_data

    def save_skeleton_data(self, skeleton_data, skeleton_file_name):
        np.save(self.data_array_path/skeleton_file_name,skeleton_data)

class MainWindow(QMainWindow):
    def __init__(self,path_to_data_folder:Path):
        super().__init__()

        self.file_manager = FileManager(path_to_recording=path_to_data_folder)

        self.resize(1256, 1029)

        self.setWindowTitle("Freemocap Data Post-processing")

        self.tab_widget = QTabWidget()

        freemocap_raw_data = self.file_manager.load_skeleton_data()

        self.main_menu_tab = MainMenu(freemocap_raw_data=freemocap_raw_data)
        self.tab_widget.addTab(self.main_menu_tab, 'Main Menu')

        self.interp_tab = InterpolationMenu(freemocap_raw_data = freemocap_raw_data)
        self.tab_widget.addTab(self.interp_tab, 'Interpolation')
        # layout.addWidget(self.main_menu)

        self.filter_tab = FilteringMenu(freemocap_raw_data=freemocap_raw_data)
        self.tab_widget.addTab(self.filter_tab, 'Filtering')
        
        self.setCentralWidget(self.tab_widget)

        self.main_menu_tab.save_skeleton_data_signal.connect(self.file_manager.save_skeleton_data)


        f = 2


class InterpolationMenu(QWidget):
    def __init__(self, freemocap_raw_data:np.ndarray):
        super().__init__()
        layout = QVBoxLayout()

        
        self.setStyleSheet(groupbox_stylesheet)

        self.freemocap_raw_data = freemocap_raw_data
        self.processed_freemocap_data = None

        self.time_series_groupbox = self.create_time_series_groupbox()
        self.interpolation_param_tree_groupbox = self.create_interpolation_groupbox()

        layout.addWidget(self.time_series_groupbox)
        layout.addWidget(self.interpolation_param_tree_groupbox)
    
        self.run_interpolation_button = QPushButton('Run Interpolation')
        self.run_interpolation_button.clicked.connect(self.run_interpolation_task)
        layout.addWidget(self.run_interpolation_button)

        self.update_timeseries_plot()

        self.setLayout(layout)
        self.connect_signals_to_slots()

    def create_time_series_groupbox(self):
        groupbox = QGroupBox("View time series for a selected marker")
        time_series_layout = QVBoxLayout()
        self.marker_selector_widget = MarkerSelectorWidget()
        time_series_layout.addWidget(self.marker_selector_widget)
        self.time_series_plotter_widget = TimeSeriesPlotterWidget()
        time_series_layout.addWidget(self.time_series_plotter_widget)
        groupbox.setLayout(time_series_layout)
        return groupbox

    def create_interpolation_groupbox(self):
        groupbox = QGroupBox("Interpolation Parameters")
        interpolation_params_layout = QVBoxLayout()
        self.interpolation_param_tree = create_interpolation_parameter_tree()
        interpolation_params_layout.addWidget(self.interpolation_param_tree)
        groupbox.setLayout(interpolation_params_layout)
        return groupbox

    def update_timeseries_plot(self, reset_axes = True):
        self.time_series_plotter_widget.update_plot(marker_to_plot=self.marker_selector_widget.current_marker, original_freemocap_data=self.freemocap_raw_data , processed_freemocap_data=self.processed_freemocap_data,reset_axes = reset_axes)

    def connect_signals_to_slots(self):
        self.marker_selector_widget.marker_to_plot_updated_signal.connect(lambda: self.update_timeseries_plot(reset_axes=True))

    def run_interpolation_task(self):
        self.worker_thread = TaskWorkerThread(raw_skeleton_data=self.freemocap_raw_data, task_list=['interpolating'])
        self.worker_thread.start()
        self.worker_thread.all_tasks_finished_signal.connect(self.handle_interpolation_result)

    def handle_interpolation_result(self, task_results: dict):
        self.processed_freemocap_data = task_results['interpolating']['result']
        self.update_timeseries_plot(reset_axes=False)
       

class FilteringMenu(QWidget):
    def __init__(self, freemocap_raw_data:np.ndarray):
        super().__init__()

        self.setStyleSheet(groupbox_stylesheet)

        layout = QVBoxLayout()
        self.freemocap_raw_data = freemocap_raw_data
        self.processed_freemocap_data = None

        # Timeseries and marker selector groupbox
        self.time_series_groupbox = self.create_time_series_groupbox()
        self.filter_param_tree_groupbox = self.create_filtering_groupbox()

        layout.addWidget(self.time_series_groupbox)
        layout.addWidget(self.filter_param_tree_groupbox)

        self.run_filter_button = QPushButton('Run Filter')
        self.run_filter_button.clicked.connect(self.run_filter_task)
        layout.addWidget(self.run_filter_button)

        self.update_timeseries_plot()

        self.setLayout(layout)
        self.connect_signals_to_slots()

    def create_time_series_groupbox(self):
        groupbox = QGroupBox("View time series for a selected marker")
        time_series_layout = QVBoxLayout()
        self.marker_selector_widget = MarkerSelectorWidget()
        time_series_layout.addWidget(self.marker_selector_widget)
        self.time_series_plotter_widget = TimeSeriesPlotterWidget()
        time_series_layout.addWidget(self.time_series_plotter_widget)
        groupbox.setLayout(time_series_layout)
        return groupbox
    
    def create_filtering_groupbox(self):
        groupbox = QGroupBox("Filtering Parameters")
        filter_params_layout = QVBoxLayout()
        self.filter_param_tree = create_filter_parameter_tree()
        filter_params_layout.addWidget(self.filter_param_tree)
        groupbox.setLayout(filter_params_layout)
        return groupbox

    def update_timeseries_plot(self, reset_axes = True):
        self.time_series_plotter_widget.update_plot(marker_to_plot=self.marker_selector_widget.current_marker, original_freemocap_data=self.freemocap_raw_data , processed_freemocap_data=self.processed_freemocap_data,reset_axes = reset_axes)

    def connect_signals_to_slots(self):
        self.marker_selector_widget.marker_to_plot_updated_signal.connect(lambda: self.update_timeseries_plot(reset_axes=True))
    
    def run_filter_task(self):
        self.worker_thread = TaskWorkerThread(raw_skeleton_data=self.freemocap_raw_data, task_list=['interpolating', 'filtering'])
        self.worker_thread.start()
        self.worker_thread.all_tasks_finished_signal.connect(self.handle_filter_result)

    def handle_filter_result(self, task_results: dict):
        self.processed_freemocap_data = task_results['filtering']['result']
        self.update_timeseries_plot(reset_axes=False)
       

class MainMenu(QWidget):
    
    save_skeleton_data_signal = pyqtSignal(object,object)
    def __init__(self,freemocap_raw_data:np.ndarray):
        super().__init__()
        self.task_list = ['interpolation', 'filtering', 'finding good frame', 'skeleton rotation', 'results visualization', 'data saved']
        layout = QVBoxLayout()

        self.setStyleSheet(groupbox_stylesheet)
        
        self.freemocap_raw_data = freemocap_raw_data

        led_groupbox = self.create_led_groupbox()
        layout.addWidget(led_groupbox)

        skeleton_viewer_groupbox = self.create_skeleton_viewer_groupbox()
        layout.addWidget(skeleton_viewer_groupbox)

        parameter_groupbox = self.create_parameter_groupbox()
        layout.addWidget(parameter_groupbox)

        self.connect_signals_to_slots()

        self.skeleton_viewers_container.plot_raw_skeleton(self.freemocap_raw_data)

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

        self.worker_thread = TaskWorkerThread(raw_skeleton_data=self.freemocap_raw_data, task_list=self.task_list)
        self.worker_thread.start()
        self.worker_thread.task_running_signal.connect(self.handle_task_started)
        self.worker_thread.task_completed_signal.connect(self.handle_task_completed)
        self.worker_thread.all_tasks_finished_signal.connect(self.handle_plotting)

    def handle_task_started(self,task):
        self.led_container.change_led_to_task_is_running_color(task)

    def handle_task_completed(self,task):
        self.led_container.change_led_to_task_is_finished_color(task)

    def save_skeleton_data(self):
        # file_path_to_save = 
        final_skeleton = self.get_final_processed_skeleton()
        skeleton_save_file_name = self.save_entry.text()
        self.save_skeleton_data_signal.emit(final_skeleton,skeleton_save_file_name)
        self.handle_task_completed('data saved')


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

        self.handle_task_completed('results visualization')


if __name__ == "__main__":
    
    path_to_freemocap_session_folder = Path(r'D:\ValidationStudy2022\FreeMocap_Data\sesh_2022-05-24_16_10_46_JSM_T1_WalkRun')
    #path_to_freemocap_session_folder = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\recording_15_20_51_gmt-4__brit_half_inch')
    #path_to_freemocap_session_folder = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\recording_15_22_56_gmt-4__brit_one_inch')

    # path_to_freemocap_session_folder = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\recording_15_19_00_gmt-4__brit_baseline')
    # freemocap_raw_data = np.load(path_to_freemocap_session_folder/'output_data'/'raw_data'/'mediapipe3dData_numFrames_numTrackedPoints_spatialXYZ.npy')

    # freemocap_raw_data = np.load(path_to_freemocap_session_folder/'DataArrays'/'mediaPipeSkel_3d.npy')
    # freemocap_raw_data = freemocap_raw_data[:,0:33,:]


    path_to_data_folder = Path(r'D:\ValidationStudy2022\FreeMocap_Data\sesh_2022-05-24_16_10_46_JSM_T1_WalkRun')

    app = QApplication([])
    win = MainWindow(path_to_data_folder)
    win.show()
    app.exec()
