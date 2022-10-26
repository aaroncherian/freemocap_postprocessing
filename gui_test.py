from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QSlider, QVBoxLayout, QWidget,QLabel
from PyQt6.QtWidgets import QApplication  

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pathlib import Path
import numpy as np


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111,projection = '3d')
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self,skel3d_data):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout()

        self.slider = QSlider(Qt.Orientation.Horizontal)

        num_frames = skel3d_data.shape[0]
        self.slider.setMaximum(num_frames-1)
        layout.addWidget(self.slider)
        self.label = QLabel(str(self.slider.value()))
        layout.addWidget(self.label)
        
            
        # self.graphWidget = pg.PlotWidget()

        #hour,temperature = self.get_hour_temp()
        skel_x,skel_y,skel_z = self.get_x_y_z_data()
        self.fig = MplCanvas(self, width=5, height=4, dpi=100)
        self.ax = self.fig.figure.axes[0]

        self.mx_skel = np.nanmean(skel3d_data[:,0:33,0])
        self.my_skel = np.nanmean(skel3d_data[:,0:33,1])
        self.mz_skel = np.nanmean(skel3d_data[:,0:33,2])
        self.skel_3d_range = 900
        
        self.plot_skel(skel_x,skel_y,skel_z)

        #self.plot_graph(hour,temperature)

        #self.graphWidget.plot(hour,temperature)

        # layout.addWidget(self.graphWidget)
        self.slider.valueChanged.connect(self.replot)
        layout.addWidget(self.fig)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)
    
    def plot_skel(self,skel_x,skel_y,skel_z):
        self.ax.scatter(skel_x,skel_y,skel_z)
        self.ax.set_xlim([self.mx_skel-self.skel_3d_range, self.mx_skel+self.skel_3d_range])
        self.ax.set_ylim([self.my_skel-self.skel_3d_range, self.my_skel+self.skel_3d_range])
        self.ax.set_zlim([self.mz_skel-self.skel_3d_range, self.mz_skel+self.skel_3d_range])
        self.fig.figure.canvas.draw_idle()


    def plot_graph(self,hour,temperature):
        # self.graphWidget.plot(hour,temperature)
        self.ax.scatter(hour, temperature, [1,2,3,4,5,6,7,8,9,10])
        self.fig.figure.canvas.draw_idle()

    def get_hour_temp(self):
        hour = [1,2,3,4,5,6,7,8,9,10]
        temperature = [self.slider.value(),self.slider.value()*3,self.slider.value()*.5,32,33,31,29,32,35,45]

        return hour, temperature

    def get_x_y_z_data(self):
        skel_x = skel3d_raw_data[self.slider.value(),:,0]
        skel_y = skel3d_raw_data[self.slider.value(),:,1]
        skel_z = skel3d_raw_data[self.slider.value(),:,2]

        return skel_x,skel_y,skel_z

    def replot(self):
        #hour, temperature = self.get_hour_temp()
        skel_x,skel_y,skel_z = self.get_x_y_z_data()
        self.ax.cla()
        self.plot_skel(skel_x,skel_y,skel_z)
        self.label.setText(str(self.slider.value()))
        # self.graphWidget.clear()
        #self.plot_graph(hour,temperature)


if __name__ == "__main__":


    freemocap_data_folder_path = Path(r'C:\Users\Aaron\FreeMocap_Data')
    sessionID = 'sesh_2022-09-29_17_29_31'
    data_array_folder = 'DataArrays'
    array_name = 'mediaPipeSkel_3d.npy'


    data_array_folder_path = freemocap_data_folder_path / sessionID / data_array_folder
    skel3d_raw_data = np.load(data_array_folder_path / array_name)

    app = QApplication([])
    win = MainWindow(skel3d_raw_data)
    win.show()
    app.exec()
        # logger.info(f"`main` exited with error code: {error_code}")
        # win.close()
        # if error_code != EXIT_CODE_REBOOT:
        #     logger.info(f"Exiting...")
        #     break
        # else:
        #     logger.info("`main` exited with the 'reboot' code, so let's reboot!")