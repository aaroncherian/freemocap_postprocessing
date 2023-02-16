from freemocap_utils.freemocap_data_loader import FreeMoCapDataLoader

import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

mediapipe_indices = ['nose',
    'left_eye_inner',
    'left_eye',
    'left_eye_outer',
    'right_eye_inner',
    'right_eye',
    'right_eye_outer',
    'left_ear',
    'right_ear',
    'mouth_left',
    'mouth_right',
    'left_shoulder',
    'right_shoulder',
    'left_elbow',
    'right_elbow',
    'left_wrist',
    'right_wrist',
    'left_pinky',
    'right_pinky',
    'left_index',
    'right_index',
    'left_thumb',
    'right_thumb',
    'left_hip',
    'right_hip',
    'left_knee',
    'right_knee',
    'left_ankle',
    'right_ankle',
    'left_heel',
    'right_heel',
    'left_foot_index',
    'right_foot_index']


#path_to_session = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-01-17_13_29_22\13_30_53_gmt-5')

path_to_session = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-01-17_15_47_19\15_50_24_gmt-5')
freemocap_body_data = np.load(path_to_session/'output_data'/'mediapipe_body_3d_xyz.npy')

left_wrist_positions = freemocap_body_data[:,mediapipe_indices.index('left_wrist'),:]
right_wrist_positions = freemocap_body_data[:,mediapipe_indices.index('right_wrist'),:]

left_wrist_velocities = np.diff(left_wrist_positions,axis = 0)
right_wrist_velocities = np.diff(right_wrist_positions,axis = 0)

figure = plt.figure()
position_ax = figure.add_subplot(211)
velocity_ax = figure.add_subplot(212)

direction = 0 #x,y, or z

position_ax.set_title('Wrist Positions')
velocity_ax.set_title('Wrist Velocities')

position_ax.plot(left_wrist_positions[:,direction], color = 'b')
position_ax.plot(right_wrist_positions[:,direction], color = 'r')

velocity_ax.plot(left_wrist_velocities[:,direction], color = 'b')
velocity_ax.plot(right_wrist_velocities[:,direction], color = 'r')

left_zero_crossings = np.where(np.diff(np.sign(left_wrist_velocities[:,direction])))[0]
#velocity_ax.scatter(left_zero_crossings,left_wrist_velocities[:,direction][left_zero_crossings], marker = 'o', color = 'g')

right_zero_crossings = np.where(np.diff(np.sign(right_wrist_velocities[:,direction])))[0]
velocity_ax.scatter(right_zero_crossings,right_wrist_velocities[:,direction][right_zero_crossings], marker = 'o', color = 'g')

plt.show()
f=2