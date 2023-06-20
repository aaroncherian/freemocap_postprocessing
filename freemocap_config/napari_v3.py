import napari
import numpy as np
from qtpy.QtWidgets import QSlider, QPushButton, QVBoxLayout, QWidget
from pathlib import Path
import cv2
from rich.progress import track

def calculate_joint_acceleration(joint_positions):
    velocities = np.diff(joint_positions, axis=0)
    accelerations = np.diff(velocities, axis=0)
    magnitudes = np.linalg.norm(accelerations, axis=-1)
    return magnitudes

# def calculate_joint_velocities(joint_positions):
#     velocities = np.diff(joint_positions, axis=0)

#     # Calculate differences between consecutive velocities (accelerations)
#     accelerations = np.diff(velocities, axis=0)

#     # Calculate the magnitude of the acceleration vector for each joint
#     magnitudes = np.linalg.norm(accelerations, axis=-1)

#     return magnitudes

def detect_tracking_errors(joint_velocities, threshold):
    errors = joint_velocities > threshold
    errors_next = np.concatenate((errors[1:], np.zeros((1, errors.shape[1]), dtype=bool)))
    errors_prev = np.concatenate((np.zeros((1, errors.shape[1]), dtype=bool), errors[:-1]))
    combined_errors = np.logical_or(errors, np.logical_or(errors_next, errors_prev))
    return combined_errors

def update_and_recompute_errors(joint_positions):
    global tracking_errors

    current_frame = slider.value()
    window_size = 5  # Adjust this value to change the size of the window around the current frame

    # Update joint positions based on the current points in the points_layer
    start_frame = max(0, current_frame - window_size)
    end_frame = min(num_frames, current_frame + window_size + 1)
    for i in range(start_frame, end_frame):
        slider.setValue(i)
        joint_positions[i] = points_layer.data

    # Recompute joint velocities and tracking errors for the window around the current frame
    joint_velocities_window = calculate_joint_acceleration(joint_positions[start_frame:end_frame + 1])
    error_start_frame = start_frame + 1
    error_end_frame = end_frame
    tracking_errors[error_start_frame:error_end_frame] = detect_tracking_errors(joint_velocities_window[:], acceleration_threshold)
    # Set the slider value back to the current frame
    slider.setValue(current_frame)

    # Update the marker colors based on the new tracking errors
    update_joint_positions(slider.value())

def save_and_quit(joint_positions):

    # np.save("updated_joint_positions.npy", joint_positions)
    viewer.close()
    print(joint_positions.shape)
    f = 2

# Function to update joint positions on the points layer
def update_joint_positions(value):
    if value >= num_frames:
        print('were out of bounds')
        return
    image_layer.data = frames[value]
    viewer.layers.selection.active = points_layer
    points_layer.data = joint_positions[value]
    
    # Change the color of the markers based on the tracking errors
    marker_colors = ['red' if error else 'white' for error in tracking_errors[value]] if value < len(tracking_errors) else ['white'] * num_joints
    points_layer.face_color = marker_colors


path_to_freemocap_session_folder = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\recording_15_19_00_gmt-4__brit_baseline')
freemocap_raw_data = np.load(path_to_freemocap_session_folder/'output_data'/'raw_data'/'mediapipe2dData_numCams_numFrames_numTrackedPoints_pixelXY.npy')

freemocap_single_cam = freemocap_raw_data[0,:,0:33,0:2]

freemocap_adjusted = freemocap_single_cam[:,:,::-1]

original_joint_positions = freemocap_adjusted

joint_positions = original_joint_positions.copy()

num_frames = freemocap_single_cam.shape[0]
num_joints = freemocap_single_cam.shape[1]

joint_acceleration = calculate_joint_acceleration(joint_positions)

acceleration_threshold = 30

tracking_errors = detect_tracking_errors(joint_acceleration, acceleration_threshold)

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
# Create a QPushButton widget to trigger the update_and_recompute_errors function

# Create a Napari viewer instance
viewer = napari.Viewer()

# Add an image layer to display video frames
image_layer = viewer.add_image(frames[0], name='Video Frames')

# Add a points layer to display the joint positions
points_layer = viewer.add_points(joint_positions[0], name='Joints')
marker_colors = ['red' if error else 'white' for error in tracking_errors[0]]
points_layer.face_color = marker_colors

# Create a QSlider widget to navigate through frames
slider = QSlider()
slider.setRange(0, num_frames - 1)
slider.valueChanged.connect(update_joint_positions)

# Add the slider to the Napari viewer
viewer.window.add_dock_widget(slider, area='right', name='Frame Slider')

update_button = QPushButton("Update and Recompute Errors")
update_button.clicked.connect(lambda:update_and_recompute_errors(joint_positions))

save_and_quit_button = QPushButton("Save and Quit")
save_and_quit_button.clicked.connect(lambda:save_and_quit(joint_positions))

buttons_layout = QVBoxLayout()
buttons_layout.addWidget(update_button)
buttons_layout.addWidget(save_and_quit_button)
buttons_widget = QWidget()
buttons_widget.setLayout(buttons_layout)
viewer.window.add_dock_widget(buttons_widget, area='bottom', name='Buttons')

napari.run()

