import napari
import numpy as np
from qtpy.QtWidgets import QSlider, QPushButton
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

freemocap_adjusted = freemocap_single_cam[:,:,::-1]
# freemocap_adjusted[]

#freemocap_single_cam[:,:,1] = -freemocap_single_cam[:,:,1]
joint_positions = freemocap_adjusted

num_frames = freemocap_single_cam.shape[0]
num_joints = freemocap_single_cam.shape[1]

joint_acceleration = calculate_joint_acceleration(joint_positions)


# def detect_tracking_errors(joint_velocities, threshold):
#     errors = joint_velocities > threshold
#     errors = np.concatenate((errors[1:], np.zeros((1, errors.shape[1]), dtype=bool)))
#     return errors

def detect_tracking_errors(joint_velocities, threshold):
    errors = joint_velocities > threshold
    errors_next = np.concatenate((errors[1:], np.zeros((1, errors.shape[1]), dtype=bool)))
    errors_prev = np.concatenate((np.zeros((1, errors.shape[1]), dtype=bool), errors[:-1]))
    combined_errors = np.logical_or(errors, np.logical_or(errors_next, errors_prev))
    return combined_errors





acceleration_threshold = 35

tracking_errors = detect_tracking_errors(joint_acceleration, acceleration_threshold)

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


# angle_degrees = -90  # Replace with the desired rotation angle in degrees

# # Calculate the center of rotation (e.g., center of the video frame)
# center = np.array([frame_width / 2, frame_height / 2])

# # Rotate joint positions
# joint_positions = np.empty_like(freemocap_single_cam)
# for i, frame_joint_positions in enumerate(freemocap_single_cam):
#     joint_positions[i] = rotate_points(frame_joint_positions, angle_degrees, center)
def update_and_recompute_errors():
    global joint_positions
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



    # current_frame = slider.value()
    # # Update joint positions based on the current points in the points_layer
    # for i in track(range(num_frames)):
    #     slider.setValue(i)  # Set the slider value to the current frame, capped at num_frames - 1
    #     joint_positions[i] = points_layer.data  # Update the joint_positions array with the current frame's data


    # # Recompute joint velocities and tracking errors
    # joint_velocities = calculate_joint_velocities(joint_positions)
    # tracking_errors = detect_tracking_errors(joint_velocities, velocity_threshold)
    # f = 2
    # slider.setValue(current_frame)
    # Update the marker colors based on the new tracking errors
    # update_joint_positions(slider.value())

# Create a QPushButton widget to trigger the update_and_recompute_errors function

# Create a Napari viewer instance
viewer = napari.Viewer()

# Add an image layer to display video frames
image_layer = viewer.add_image(frames[0], name='Video Frames')

# Add a points layer to display the joint positions
points_layer = viewer.add_points(joint_positions[0], name='Joints')
marker_colors = ['red' if error else 'white' for error in tracking_errors[0]]
points_layer.face_color = marker_colors

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


# Create a QSlider widget to navigate through frames
slider = QSlider()
slider.setRange(0, num_frames - 1)
slider.valueChanged.connect(update_joint_positions)

# Add the slider to the Napari viewer
viewer.window.add_dock_widget(slider, area='right', name='Frame Slider')

update_button = QPushButton("Update and Recompute Errors")
update_button.clicked.connect(update_and_recompute_errors)
viewer.window.add_dock_widget(update_button, area='bottom', name='Update Button')



# Start Napari GUI event loop
napari.run()