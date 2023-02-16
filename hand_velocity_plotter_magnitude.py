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
joint_to_plot = 'right_wrist'
threshold = 5
direction = 0 #x,y, or z

freemocap_body_data = np.load(path_to_session/'output_data'/'mediapipe_body_3d_xyz.npy')

joint_position_og = freemocap_body_data[:,mediapipe_indices.index(joint_to_plot),:]
#joint_velocity = np.diff(joint_position_og,axis = 0)

velocity_dict = {'x':None,'y':None,'z':None}
velocity_dict_keys_list = list(velocity_dict.keys())

for direction in range(3):
    joint_position = freemocap_body_data[:,mediapipe_indices.index(joint_to_plot),direction]
    joint_velocity = np.diff(joint_position,axis = 0)
    velocity_dict[velocity_dict_keys_list[direction]] = joint_velocity

velocity_magnitude_list = []
for count in range(len(velocity_dict['x'])):
    velocity_magnitude = np.sqrt((velocity_dict['x'][count])**2 + (velocity_dict['y'][count])**2 + (velocity_dict['z'][count])**2)
    velocity_magnitude_list.append(velocity_magnitude)

# zero_crossings_frames = np.where(np.diff(np.sign(joint_velocity[:,direction])))[0]
# zero_crossings_frames = zero_crossings_frames + 1 

# thresholded_zero_crossings_frames = list(zero_crossings_frames.copy())



# for count,frame in enumerate(thresholded_zero_crossings_frames):
#     frames_to_filter_out = np.array(range(frame+1,frame+threshold))
#     thresholded_zero_crossings_frames = np.setdiff1d(thresholded_zero_crossings_frames,frames_to_filter_out)
#     f = 2


figure = plt.figure()
position_ax = figure.add_subplot(211)
velocity_ax = figure.add_subplot(212)

position_ax.set_title('Joint Position')
velocity_ax.set_title('Joint Velocity')

position_ax.plot(joint_position_og[:,0], color = 'b')
velocity_ax.plot(velocity_magnitude_list, color = 'b')
    
# velocity_ax.scatter(thresholded_zero_crossings_frames,joint_velocity[:,direction][thresholded_zero_crossings_frames], marker = 'o', color = 'g')

# velocity_ax.axhline(0)
plt.show()
f=2