
from pathlib import Path
import numpy as np

from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QHBoxLayout,QVBoxLayout

from freemocap_utils.GUI_widgets.time_series_widgets.trajectory_view_widget import TimeSeriesPlotterWidget
from freemocap_utils.GUI_widgets.time_series_widgets.marker_selector_widget import MarkerSelectorWidget

class MainWindow(QMainWindow):
    def __init__(self, freemocap_marker_data_dictionary:dict, freemocap_com_data_dictionary:dict):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout()

        widget = QWidget()

        self.freemocap_marker_data_dictionary = freemocap_marker_data_dictionary
        self.freemocap_com_data_dictionary = freemocap_com_data_dictionary

        self.marker_selector_widget = MarkerSelectorWidget()
        layout.addWidget(self.marker_selector_widget)

        self.trajectory_view_widget = TimeSeriesPlotterWidget()
        layout.addWidget(self.trajectory_view_widget)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.connect_signals_to_slots()

    def connect_signals_to_slots(self):
        self.marker_selector_widget.marker_to_plot_updated_signal.connect(lambda: self.trajectory_view_widget.update_plot(self.marker_selector_widget.current_marker,freemocap_marker_data_dictionary,freemocap_com_data_dictionary))


if __name__ == "__main__":
    
    #path_to_freemocap_session_folder = Path(r'C:\Users\Aaron\Documents\freemocap_sessions\num_Cams_validation\sesh_2022-05-24_15_55_40_JSM_T1_BOS')
    # path_to_freemocap_session_folder = Path(r'D:\ValidationStudy2022\FreeMocap_Data\sesh_2022-05-24_16_02_53_JSM_T1_NIH')
    # freemocap_data = np.load(path_to_freemocap_session_folder/'DataArrays'/'mediaPipeSkel_3d_origin_aligned.npy')

    path_to_freemocap_session_folder = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions')
    sessionID_list = ['recording_15_19_00_gmt-4__brit_baseline','recording_15_20_51_gmt-4__brit_half_inch', 'recording_15_22_56_gmt-4__brit_one_inch','recording_15_24_58_gmt-4__brit_two_inch']
    label_list = ['baseline', 'half inch lift', 'one inch lift', 'two inch lift']

    sessionID_list = ['recording_15_19_00_gmt-4__brit_baseline','recording_15_20_51_gmt-4__brit_half_inch']
    label_list = ['baseline', 'two inch lift']


    freemocap_marker_data_dictionary = {}
    freemocap_com_data_dictionary = {}

    for sessionID, label in zip(sessionID_list, label_list):
        path_to_marker_data = path_to_freemocap_session_folder/sessionID/'output_data'/'mediapipe_body_3d_xyz_transformed.npy'
        path_to_com_data = path_to_freemocap_session_folder/sessionID/'output_data'/'center_of_mass'/'total_body_center_of_mass_xyz.npy'
        freemocap_marker_data_dictionary[label] = np.load(path_to_marker_data)
        freemocap_com_data_dictionary[label] = np.load(path_to_com_data)


    f = 2


    app = QApplication([])
    win = MainWindow(freemocap_marker_data_dictionary,freemocap_com_data_dictionary)

    win.show()
    app.exec()
