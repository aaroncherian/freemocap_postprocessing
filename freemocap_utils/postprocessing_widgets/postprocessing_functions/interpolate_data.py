import numpy as np
import pandas as pd
from rich.progress import track


def interpolate_skeleton_data(skeleton_data:np.ndarray, method_to_use = 'linear', led_indicator = None) -> np.ndarray:
    """ Takes in a 3d skeleton numpy array from freemocap and interpolates missing NaN values"""
    num_frames = skeleton_data.shape[0]
    num_markers = skeleton_data.shape[1]

    freemocap_interpolated_data = np.empty((num_frames, num_markers, 3))

    for marker in track(range(num_markers), description= 'Interpolating Data'):
        this_marker_skel3d_data = skeleton_data[:,marker,:]
        df = pd.DataFrame(this_marker_skel3d_data)
        df2 = df.interpolate(method = method_to_use,axis = 0) #use pandas interpolation methods to fill in missing data
        this_marker_interpolated_skel3d_array = np.array(df2)
        #replace the remaining NaN values (the ones that often happen at the start of the recording)
        this_marker_interpolated_skel3d_array = np.where(np.isfinite(this_marker_interpolated_skel3d_array), this_marker_interpolated_skel3d_array, np.nanmean(this_marker_interpolated_skel3d_array))
        
        freemocap_interpolated_data[:,marker,:] = this_marker_interpolated_skel3d_array

    if led_indicator:
        led_indicator.set_color(1,88,91)

    return freemocap_interpolated_data
        