from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QSlider, QVBoxLayout, QWidget,QLabel, QFileDialog,QPushButton
from PyQt6.QtWidgets import QApplication  



import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pathlib import Path
import numpy as np

from build_mediapipe_skeleton import build_mediapipe_skeleton, mediapipe_indices

from anthropometric_data import segments, joint_connections, segment_COM_lengths, segment_COM_percentages, build_anthropometric_dataframe


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111,projection = '3d')
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QVBoxLayout()
        print('starting')
        self.session_folder_path = None
        self.anthropometric_info_dataframe = build_anthropometric_dataframe(segments,joint_connections,segment_COM_lengths,segment_COM_lengths)
        self.folderOpenButton = QPushButton('Load a session folder',self)
        layout.addWidget(self.folderOpenButton)
        self.folderOpenButton.clicked.connect(self.open_folder_dialog)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMaximum(0)


        layout.addWidget(self.slider)
        self.label = QLabel(str(self.slider.value()))
        layout.addWidget(self.label)
        
        self.initialize_skeleton_plot()

        self.slider.valueChanged.connect(self.replot)
        layout.addWidget(self.fig)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def open_folder_dialog(self):
        
        self.folder_diag = QFileDialog()
        self.session_folder_path  = QFileDialog.getExistingDirectory(None,"Choose a session")

        if self.session_folder_path:
            self.session_folder_path = Path(self.session_folder_path)
            data_array_folder_path = self.session_folder_path / 'DataArrays'/'mediaPipeSkel_3d.npy'

            self.skel3d_data = np.load(data_array_folder_path)

            
            self.mediapipe_bone_connections = build_mediapipe_skeleton(self.skel3d_data,self.anthropometric_info_dataframe,mediapipe_indices)
            self.reset_plot()
            self.reset_slider()

            


    def initialize_skeleton_plot(self):
        #self.skel_x,self.skel_y,self.skel_z = self.get_x_y_z_data()
        self.fig = MplCanvas(self, width=5, height=4, dpi=100)
        self.ax = self.fig.figure.axes[0]

    def reset_plot(self):
        self.ax.cla()
        self.calculate_axes_means(self.skel3d_data)
        self.skel_x,self.skel_y,self.skel_z = self.get_x_y_z_data()
        self.plot_skel(self.skel_x,self.skel_y,self.skel_z)

    def reset_slider(self):
        num_frames = self.skel3d_data.shape[0]
        self.slider_max = num_frames -1
        self.slider.setMaximum(self.slider_max)

        self.num_frames = num_frames

    def calculate_axes_means(self,skeleton_3d_data):
        self.mx_skel = np.nanmean(skeleton_3d_data[:,0:33,0])
        self.my_skel = np.nanmean(skeleton_3d_data[:,0:33,1])
        self.mz_skel = np.nanmean(skeleton_3d_data[:,0:33,2])
        self.skel_3d_range = 900

    def plot_skel(self,skel_x,skel_y,skel_z):
        self.ax.scatter(skel_x,skel_y,skel_z)
        self.plot_skeleton_bones()
        self.ax.set_xlim([self.mx_skel-self.skel_3d_range, self.mx_skel+self.skel_3d_range])
        self.ax.set_ylim([self.my_skel-self.skel_3d_range, self.my_skel+self.skel_3d_range])
        self.ax.set_zlim([self.mz_skel-self.skel_3d_range, self.mz_skel+self.skel_3d_range])

        self.fig.figure.canvas.draw_idle()

    def plot_skeleton_bones(self):
            frame = self.slider.value()
            this_frame_skeleton_data = self.mediapipe_bone_connections[frame]
            for segment in this_frame_skeleton_data.keys():
                prox_joint = this_frame_skeleton_data[segment][0] 
                dist_joint = this_frame_skeleton_data[segment][1]
                
                bone_x,bone_y,bone_z = [prox_joint[0],dist_joint[0]],[prox_joint[1],dist_joint[1]],[prox_joint[2],dist_joint[2]] 

                self.ax.plot(bone_x,bone_y,bone_z)

    def get_x_y_z_data(self):
        skel_x = self.skel3d_data[self.slider.value(),:,0]
        skel_y = self.skel3d_data[self.slider.value(),:,1]
        skel_z = self.skel3d_data[self.slider.value(),:,2]

        return skel_x,skel_y,skel_z

    def replot(self):
        skel_x,skel_y,skel_z = self.get_x_y_z_data()
        self.ax.cla()
        self.plot_skel(skel_x,skel_y,skel_z)
        self.label.setText(str(self.slider.value()))


if __name__ == "__main__":


    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()
        # logger.info(f"`main` exited with error code: {error_code}")
        # win.close()
        # if error_code != EXIT_CODE_REBOOT:
        #     logger.info(f"Exiting...")
        #     break
        # else:
        #     logger.info("`main` exited with the 'reboot' code, so let's reboot!")