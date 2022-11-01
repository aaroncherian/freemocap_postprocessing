from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QSlider, QGridLayout, QWidget,QLabel, QFileDialog,QPushButton
from PyQt6.QtWidgets import QApplication  



import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.colors as mcolors

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pathlib import Path
import numpy as np

#from build_mediapipe_skeleton import build_mediapipe_skeleton, mediapipe_indices

#from anthropometric_data import segments, joint_connections, segment_COM_lengths, segment_COM_percentages, build_anthropometric_dataframe

from skeleton_builder_v3 import mediapipe_indices,mediapipe_connections,reprojection_error_mediapipe_connections,build_skeleton,get_number_of_tracked_markers, sum_reprojection_error_by_limb_reformat

class Mpl3DPlotCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=4, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111,projection = '3d')
        super(Mpl3DPlotCanvas, self).__init__(fig)

class MplReprojectionErrorCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.sum_plot_axes = fig.add_subplot(211)
        self.limb_plot_axes = fig.add_subplot(212)
        super(MplReprojectionErrorCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QGridLayout()
        print('starting')
        self.session_folder_path = None
        #self.anthropometric_info_dataframe = build_anthropometric_dataframe(segments,joint_connections,segment_COM_lengths,segment_COM_lengths)
        self.folderOpenButton = QPushButton('Load a session folder',self)
        layout.addWidget(self.folderOpenButton,0,0)
        self.folderOpenButton.clicked.connect(self.open_folder_dialog)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMaximum(0)


        layout.addWidget(self.slider,1,0,1,1)
        self.label = QLabel(str(self.slider.value()))
        layout.addWidget(self.label,2,0)
        
        self.initialize_skeleton_plot()
        self.initialize_reprojection_error_plots()

        self.slider.valueChanged.connect(self.replot)
        layout.addWidget(self.fig,3,0)
        layout.addWidget(self.repro_error_fig,3,1)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def open_folder_dialog(self):
        
        self.folder_diag = QFileDialog()
        self.session_folder_path  = QFileDialog.getExistingDirectory(None,"Choose a session")

        if self.session_folder_path:
            self.session_folder_path = Path(self.session_folder_path)
            skeleton_data_folder_path = self.session_folder_path / 'DataArrays'/'mediaPipeSkel_3d.npy'
            skelton_repro_error_data_folder_path = self.session_folder_path / 'DataArrays'/'mediaPipeSkel_reprojErr.npy'
            self.skel3d_data = np.load(skeleton_data_folder_path)
            self.skel_repro_error_data = np.load(skelton_repro_error_data_folder_path)

            self.mediapipe_skeleton = build_skeleton(self.skel3d_data,mediapipe_indices,mediapipe_connections)
            
            self.reprojection_error_by_limb_data = sum_reprojection_error_by_limb_reformat(self.skel_repro_error_data,mediapipe_indices,reprojection_error_mediapipe_connections)

            self.tracked_markers = get_number_of_tracked_markers(self.skel_repro_error_data,mediapipe_indices)

            self.num_frames = self.skel3d_data.shape[0]
            self.reset_slider()
            self.reset_skeleton_3d_plot()
            self.reset_repro_error_plots()

            

            
    def initialize_reprojection_error_plots(self):
        self.repro_error_fig = MplReprojectionErrorCanvas(self, width=12, height=6, dpi=100)
        self.repro_sum_fig_axes = self.repro_error_fig.figure.axes[0]
        self.repro_limb_fig_axes = self.repro_error_fig.figure.axes[1]

    def initialize_skeleton_plot(self):
        #self.skel_x,self.skel_y,self.skel_z = self.get_x_y_z_data()
        self.fig = Mpl3DPlotCanvas(self, width=5, height=4, dpi=100)
        self.ax = self.fig.figure.axes[0]

    def reset_skeleton_3d_plot(self):
        self.ax.cla()
        self.calculate_axes_means(self.skel3d_data)
        self.skel_x,self.skel_y,self.skel_z = self.get_x_y_z_data()
        self.plot_skel(self.skel_x,self.skel_y,self.skel_z)

    def reset_repro_error_plots(self):
        self.repro_limb_fig_axes.cla()
        self.repro_sum_fig_axes.cla()
        self.repro_sum_data = self.get_reprojection_error_sum_data()
        self.plot_tracked_markers(self.tracked_markers)
        self.plot_repro_error_limbs(self.reprojection_error_by_limb_data)
        f = 2

    def reset_slider(self):
        self.slider_max = self.num_frames -1
        self.slider.setValue(0)
        self.slider.setMaximum(self.slider_max)

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

    def plot_tracked_markers(self,num_tracked_markers):
        self.repro_sum_fig_axes.plot(num_tracked_markers)
        self.repro_sum_fig_axes.set_ylim([0,35])
        self.vline = self.repro_sum_fig_axes.axvline(self.slider.value(), c = 'k')
        self.repro_error_fig.figure.canvas.draw_idle()

    def update_repro_error_sum_vline(self):
        self.vline.set_xdata(self.slider.value())
        self.repro_error_fig.figure.canvas.draw()

        

    def plot_repro_error_limbs(self,reprojection_error_by_limb_data):

        for limb in reprojection_error_by_limb_data:
            self.repro_limb_fig_axes.plot(reprojection_error_by_limb_data[limb])
        
        self.repro_error_fig.figure.canvas.draw_idle()

    def plot_skeleton_bones(self):
            frame = self.slider.value()
            this_frame_skeleton_data = self.mediapipe_skeleton[frame]
            cmap, norm = mcolors.from_levels_and_colors([0, 2, 5, 6], ['red', 'green', 'blue'])
            for connection in this_frame_skeleton_data.keys():
                line_start_point = this_frame_skeleton_data[connection][0] 
                line_end_point = this_frame_skeleton_data[connection][1]
                
                bone_x,bone_y,bone_z = [line_start_point[0],line_end_point[0]],[line_start_point[1],line_end_point[1]],[line_start_point[2],line_end_point[2]] 

                self.ax.plot(bone_x,bone_y,bone_z)

    def get_x_y_z_data(self):
        skel_x = self.skel3d_data[self.slider.value(),:,0]
        skel_y = self.skel3d_data[self.slider.value(),:,1]
        skel_z = self.skel3d_data[self.slider.value(),:,2]

        return skel_x,skel_y,skel_z

    def get_reprojection_error_sum_data(self):
        repro_error_sum_data = np.empty([self.num_frames,1])
        for frame in range(self.num_frames):
            this_frame_sum = np.nansum(self.skel_repro_error_data[frame,0:33])
            repro_error_sum_data[frame] = this_frame_sum
        return repro_error_sum_data



    def replot(self):
        skel_x,skel_y,skel_z = self.get_x_y_z_data()
        self.ax.cla()
        self.repro_limb_fig_axes.cla()
        self.plot_skel(skel_x,skel_y,skel_z)
        self.update_repro_error_sum_vline()
        self.plot_repro_error_limbs(self.reprojection_error_by_limb_data)
        #self.plot_repro_error_sum(self.repro_sum_data)
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