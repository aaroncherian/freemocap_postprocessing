import cv2
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog

from pathlib import Path

class SingleVideoWorker():
    def __init__(self, video_path: Path):
        self.video_path = video_path

        self.video_capture_object = self.load_video_from_path()

    def load_video_from_path(self):
        video_capture_object = cv2.VideoCapture(str(self.video_path))
        return video_capture_object

    def run_worker(self,frame_number):
        self.set_video_to_frame(frame_number)
        frame = self.read_frame_from_video()
        self.pixmap = self.convert_frame_to_pixmap(frame)
        
    def set_video_to_frame(self,frame_number):
        self.video_capture_object.set(cv2.CAP_PROP_POS_FRAMES,frame_number)
    
    def read_frame_from_video(self):
        ret, frame = self.video_capture_object.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    
    def convert_frame_to_pixmap(self,frame):
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format.Format_RGB888)
        QtGui.QPixmap()
        pix = QtGui.QPixmap.fromImage(img)
        resized_pixmap = pix.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        # self.video_frame.setPixmap(resizeImage)
        return resized_pixmap
        
    def display_first_frame(self, video_frame_widget, pixmap):
        self.video_frame_widget = video_frame_widget
        self.video_frame_widget.setPixmap(pixmap)







class LoadVideo(QWidget):
    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout (self._layout)

        self.videoLoadButton = QPushButton('Load a video',self)
        self.videoLoadButton.setEnabled(False)
        self._layout.addWidget(self.videoLoadButton)
        self.videoLoadButton.clicked.connect(self.load_video)

        self.video_is_loaded = False
    def set_session_folder_path(self,session_folder_path:Path):
        self.session_folder_path = session_folder_path

    def load_video(self):
        self.folder_diag = QFileDialog()
        self.video_path,filter  = QFileDialog.getOpenFileName(self, 'Open file', directory = str(self.session_folder_path))

        if self.video_path:
            self.vid_capture_object = cv2.VideoCapture(str(self.video_path))
            self.video_is_loaded = True

        
        f = 2



class MultiVideoDisplay(QWidget):
    def __init__(self):
        super().__init__()

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.videoFolderLoadButton = QPushButton('Load a folder of videos',self)
        self.videoFolderLoadButton.setEnabled(False)
        self._layout.addWidget(self.videoFolderLoadButton)
        self.videoFolderLoadButton.clicked.connect(self.load_video_folder)

        self.are_videos_loaded = False

    def set_session_folder_path(self,session_folder_path:Path):
        self.session_folder_path = session_folder_path

    def load_video_folder(self):
        self.folder_diag = QFileDialog()
        self.video_folder_path  = QFileDialog.getExistingDirectory(None,"Choose a folder of videos")
        self.list_of_video_paths, self.number_of_videos = self.create_list_of_video_paths(self.video_folder_path)
        self.generate_video_display(self.list_of_video_paths,self.number_of_videos)

        self.are_videos_loaded = True
    
    def create_list_of_video_paths(self,path_to_video_folder:Path):
        list_of_video_paths = list(Path(path_to_video_folder).glob('*.mp4'))
        number_of_videos = len(list_of_video_paths)
        return list_of_video_paths, number_of_videos

    def generate_video_display(self,list_of_video_paths:list,number_of_videos:int):

        self.video_widget_dictionary = self.generate_video_workers(list_of_video_paths)
        self.label_widget_dictionary = self.create_label_widgets_for_videos(number_of_videos)
        self.add_widgets_to_layout()

        return self.video_widget_dictionary, self.label_widget_dictionary

    def generate_video_workers(self, list_of_video_paths:list):

        self.video_widget_dictionary = {}

        for count, video_path in enumerate(list_of_video_paths):
            self.video_widget_dictionary[count] = SingleVideoWorker(video_path)

        return self.video_widget_dictionary
        f = 2 

    def create_label_widgets_for_videos(self,number_of_videos):
        label_widget_dictionary = {}
        for x in range(number_of_videos):
            label_widget_dictionary[x] = QLabel('test')

        self.number_of_videos = number_of_videos
        
        return label_widget_dictionary

    def add_widgets_to_layout(self):

        for widget in self.label_widget_dictionary:
            self._layout.addWidget(self.label_widget_dictionary[widget])

    def update_display(self, frame_number:int):
        for x in range(self.number_of_videos):
            this_vid_worker = self.video_widget_dictionary[x]
            this_vid_worker.run_worker(frame_number)
            this_vid_worker.display_first_frame(self.label_widget_dictionary[x],this_vid_worker.pixmap) 










class VideoCapture(QWidget):
    def __init__(self):
        super().__init__()
        # self.cap = cv2.VideoCapture(str(filename))

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

    

        self.video_loader = LoadVideo()
        self._layout.addWidget(self.video_loader)

        self.video_frame = QLabel()
        self._layout.addWidget(self.video_frame)
        # parent.layout.addWidget(self.video_frame)
    #
    def set_frame(self,frame_number:int):
        self.video_loader.vid_capture_object.set(cv2.CAP_PROP_POS_FRAMES,frame_number)
        ret, frame = self.video_loader.vid_capture_object.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format.Format_RGB888)

        QtGui.QPixmap()
        pix = QtGui.QPixmap.fromImage(img)
        resizeImage = pix.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
        self.video_frame.setPixmap(resizeImage)

        f = 2

    # def show_frame(self, frame_number: int):
    #     self.cap.set(2,frame_number)
    #     ret, frame = self.cap.read()
    #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format.Format_RGB888)
    #
    #     QtGui.QPixmap()
    #     pix = QtGui.QPixmap.fromImage(img)
    #     resizeImage = pix.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
    #     self.video_frame.setPixmap(resizeImage)
    #     f=2

