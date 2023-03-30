
from pathlib import Path
import numpy as np

from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QHBoxLayout,QVBoxLayout

from freemocap_utils.GUI_widgets.time_series_widgets.trajectory_view_widget import TimeSeriesPlotterWidget
from freemocap_utils.GUI_widgets.time_series_widgets.marker_selector_widget import MarkerSelectorWidget

class MainWindow(QMainWindow):
    def __init__(self, freemocap_data:np.ndarray):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout()

        widget = QWidget()

        self.freemocap_data = freemocap_data

        self.marker_selector_widget = MarkerSelectorWidget()
        layout.addWidget(self.marker_selector_widget)

        self.trajectory_view_widget = TimeSeriesPlotterWidget()
        layout.addWidget(self.trajectory_view_widget)

        widget.setLayout(layout)
        self.setCentralWidget(widget)
        path_to_freemocap_session_folder = Path(r'D:\ValidationStudy2022\FreeMocap_Data\sesh_2022-05-24_16_02_53_JSM_T1_NIH')
        self.freemocap_com_data = np.load(path_to_freemocap_session_folder/'DataArrays'/'totalBodyCOM_frame_XYZ.npy')

        self.connect_signals_to_slots()

    def connect_signals_to_slots(self):
        self.marker_selector_widget.marker_to_plot_updated_signal.connect(lambda: self.trajectory_view_widget.update_plot(self.marker_selector_widget.current_marker,self.freemocap_data, self.freemocap_com_data))


if __name__ == "__main__":
    
    #path_to_freemocap_session_folder = Path(r'C:\Users\Aaron\Documents\freemocap_sessions\num_Cams_validation\sesh_2022-05-24_15_55_40_JSM_T1_BOS')
    path_to_freemocap_session_folder = Path(r'D:\ValidationStudy2022\FreeMocap_Data\sesh_2022-05-24_16_02_53_JSM_T1_NIH')
    freemocap_data = np.load(path_to_freemocap_session_folder/'DataArrays'/'mediaPipeSkel_3d_origin_aligned.npy')

    app = QApplication([])
    win = MainWindow(freemocap_data)

    win.show()
    app.exec()
