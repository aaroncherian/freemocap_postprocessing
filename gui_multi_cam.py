from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QApplication, QHBoxLayout,QVBoxLayout

from GUI_widgets.skeleton_view_widget import SkeletonViewWidget
from GUI_widgets.slider_widget import FrameCountSlider
from GUI_widgets.multi_camera_capture_widget import MultiVideoDisplay

from pathlib import Path
from glob import glob

import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        
        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        multi_video_display = MultiVideoDisplay()
        layout.addWidget(multi_video_display)

        test_path_to_folder = Path(r'D:\freemocap2022\FreeMocap_Data\sesh_2022-09-29_15_34_50\testing_synced_videos')
        list_of_video_paths = self.create_list_of_video_paths(test_path_to_folder)
        number_of_videos = len(list_of_video_paths)

        video_worker_dict, label_widget_dict = multi_video_display.generate_video_display(list_of_video_paths,number_of_videos)

        multi_video_display.update_display(0)
        # for x in range(number_of_videos):
        #     this_vid_worker = video_worker_dict[x]
        #     this_vid_worker.run_worker(500)
        #     this_vid_worker.display_first_frame(label_widget_dict[x],this_vid_worker.pixmap) 



        f = 2

    def create_list_of_video_paths(self,path_to_video_folder:Path):

        # list_of_paths = os.listdir(path_to_video_folder)
        list_of_paths = list(Path(path_to_video_folder).glob('*.mp4'))
        return list_of_paths






# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("My App")

#         layout = QHBoxLayout()

#         widget = QWidget()


#         slider_and_skeleton_layout = QVBoxLayout()

#         self.frame_count_slider = FrameCountSlider()
#         slider_and_skeleton_layout.addWidget(self.frame_count_slider)

#         self.skeleton_view_widget = SkeletonViewWidget()
#         self.skeleton_view_widget.setFixedSize(self.skeleton_view_widget.size())
#         slider_and_skeleton_layout.addWidget(self.skeleton_view_widget)
        
#         layout.addLayout(slider_and_skeleton_layout)

#         self.camera_view_widget = VideoCapture()
#         layout.addWidget(self.camera_view_widget)
#         self.camera_view_widget.setFixedSize(self.skeleton_view_widget.size())

#         widget.setLayout(layout)
#         self.setCentralWidget(widget)

#         self.connect_signals_to_slots()

#     def connect_signals_to_slots(self):
#         self.frame_count_slider.slider.valueChanged.connect(lambda: self.skeleton_view_widget.replot(self.frame_count_slider.slider.value()))

#         self.skeleton_view_widget.session_folder_loaded_signal.connect(lambda: self.frame_count_slider.set_slider_range(self.skeleton_view_widget.num_frames))
#         self.skeleton_view_widget.session_folder_loaded_signal.connect(lambda: self.camera_view_widget.video_loader.videoLoadButton.setEnabled(True))
#         self.skeleton_view_widget.session_folder_loaded_signal.connect(lambda: self.camera_view_widget.video_loader.set_session_folder_path(self.skeleton_view_widget.session_folder_path))

 
#         self.frame_count_slider.slider.valueChanged.connect(lambda: self.camera_view_widget.set_frame(self.frame_count_slider.slider.value()) if (self.camera_view_widget.video_loader.video_is_loaded) else NotImplemented)


        
if __name__ == "__main__":

    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()
