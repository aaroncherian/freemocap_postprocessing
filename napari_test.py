import napari
import numpy as np
from qtpy.QtWidgets import QSlider
from pathlib import Path
import cv2

def rotate_points(points, angle_degrees, center=None):
    # Convert angle from degrees to radians
    angle_rad = np.deg2rad(angle_degrees)

    # Calculate the rotation matrix
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])

    # If a center is provided, translate points before rotating
    if center is not None:
        points = points - center

    # Rotate points using the rotation matrix
    rotated_points = points @ rotation_matrix.T

    # If a center is provided, translate points back after rotating
    if center is not None:
        rotated_points = rotated_points + center

    return rotated_points

path_to_freemocap_session_folder = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\recording_15_19_00_gmt-4__brit_baseline')
freemocap_raw_data = np.load(path_to_freemocap_session_folder/'output_data'/'raw_data'/'mediapipe2dData_numCams_numFrames_numTrackedPoints_pixelXY.npy')

freemocap_single_cam = freemocap_raw_data[0,:,0:33,0:2]

num_frames = freemocap_single_cam.shape[0]
num_joints = freemocap_single_cam.shape[1]


f =2 


video_file = r"C:\Users\aaron\FreeMocap_Data\recording_sessions\recording_15_19_00_gmt-4__brit_baseline\synchronized_videos\Camera_000_synchronized.mp4"
cap = cv2.VideoCapture(video_file)
frames = []
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
cap.release()
frames = np.array(frames)


angle_degrees = -90  # Replace with the desired rotation angle in degrees

# Calculate the center of rotation (e.g., center of the video frame)
center = np.array([frame_width / 2, frame_height / 2])

# Rotate joint positions
joint_positions = np.empty_like(freemocap_single_cam)
for i, frame_joint_positions in enumerate(freemocap_single_cam):
    joint_positions[i] = rotate_points(frame_joint_positions, angle_degrees, center)


# Create a Napari viewer instance
viewer = napari.Viewer()

# Add an image layer to display video frames
# image_layer = viewer.add_image(frames[0], name='Video Frames')

# Add a points layer to display the joint positions
points_layer = viewer.add_points(joint_positions[0], name='Joints')

# Function to update joint positions on the points layer
def update_joint_positions(value):
    #image_layer.data = frames[value]
    points_layer.data = joint_positions[value]

# Create a QSlider widget to navigate through frames
slider = QSlider()
slider.setRange(0, num_frames - 1)
slider.valueChanged.connect(update_joint_positions)

# Add the slider to the Napari viewer
viewer.window.add_dock_widget(slider, area='right', name='Frame Slider')

# Start Napari GUI event loop
napari.run()