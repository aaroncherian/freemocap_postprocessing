from freemocap_utils.freemocap_data_loader import FreeMoCapDataLoader

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from pathlib import Path

path_to_session = None
#path_to_session = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-01-17_13_29_22\13_30_53_gmt-5')
#path_to_session = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-01-17_15_47_19\15_50_24_gmt-5')

joint_to_plot = 'left_wrist'
direction = 0 #x = 0,y = 1, z = 2
threshold_to_ignore_next_crossing = 5

#set both frames to be None if you want to plot the whole thing
start_frame = None
end_frame = None

show_plot = True
save_data = True

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



freemocap_body_data = np.load(path_to_session/'output_data'/'mediapipe_body_3d_xyz.npy')

if start_frame == None or end_frame == None:
    joint_position = freemocap_body_data[:,mediapipe_indices.index(joint_to_plot),:]
else:
    joint_position = freemocap_body_data[start_frame:end_frame,mediapipe_indices.index(joint_to_plot),:]

joint_velocity = np.diff(joint_position,axis = 0)
zero_crossings_frames = np.where(np.diff(np.sign(joint_velocity[:,direction])))[0]
#zero_crossings_frames = zero_crossings_frames + 1 

thresholded_zero_crossings_frames = list(zero_crossings_frames.copy())


for count,frame in enumerate(thresholded_zero_crossings_frames):
    frames_to_filter_out = np.array(range(frame+1,frame+threshold_to_ignore_next_crossing))
    thresholded_zero_crossings_frames = np.setdiff1d(thresholded_zero_crossings_frames,frames_to_filter_out)
    f = 2

slopes_of_lines = np.diff(np.sign(joint_velocity[:,direction]))[thresholded_zero_crossings_frames]

signs_of_lines = slopes_of_lines.copy()

for element in range(len(slopes_of_lines)):
    slope = int(slopes_of_lines[element])
    if slope > 0:
        signs_of_lines[element] = 1
    elif slope  < 0:
        signs_of_lines[element] = -1
    else:
        signs_of_lines[element] = slope

if show_plot == True:
    figure = plt.figure()
    position_ax = figure.add_subplot(211)
    velocity_ax = figure.add_subplot(212)


    position_ax.set_title('Joint Position')
    velocity_ax.set_title('Joint Velocity')


    velocity_ax.axhline(0, alpha = .6, color = 'r')

    position_ax.plot(joint_position[:,direction], color = 'b')
    velocity_ax.plot(joint_velocity[:,direction], '.-', color = 'b')
        
    velocity_ax.scatter(thresholded_zero_crossings_frames,joint_velocity[:,direction][thresholded_zero_crossings_frames], marker = 'o', color = 'g')

    plt.show()

if save_data == True:

    if start_frame is not None: #need to adjust all of the zero crossing frames by the starting frame, if you choose a later starting frame 
        thresholded_zero_crossings_frames = thresholded_zero_crossings_frames + start_frame

    zero_crossing_frames_and_line_slopes = np.array([thresholded_zero_crossings_frames,signs_of_lines])
    np.save(path_to_session/'output_data'/'zero_crossing_frames_and_line_slopes.npy',zero_crossing_frames_and_line_slopes)

    row_values = ['zero_crossing_frames', 'slopes_of_lines']
    zero_crossing_and_slopes_dataframe = pd.DataFrame(np.vstack((thresholded_zero_crossings_frames,signs_of_lines)),index = row_values).T
    zero_crossing_and_slopes_dataframe.to_csv(path_to_session/'output_data'/'zero_crossing_frames_and_line_slopes.csv')



