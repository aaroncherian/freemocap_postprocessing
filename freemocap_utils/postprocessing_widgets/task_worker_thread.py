
from freemocap_utils.postprocessing_widgets.parameter_widgets import interpolation_params, filter_params, good_frame_finder_params, rotating_params
from freemocap_utils.postprocessing_widgets.postprocessing_functions.interpolate_data import interpolate_skeleton_data
from freemocap_utils.postprocessing_widgets.postprocessing_functions.filter_data import filter_skeleton_data
from freemocap_utils.postprocessing_widgets.postprocessing_functions.good_frame_finder import find_good_frame
from freemocap_utils.postprocessing_widgets.postprocessing_functions.rotate_skeleton import align_skeleton_with_origin

from freemocap_utils.mediapipe_skeleton_builder import mediapipe_indices

from PyQt6.QtCore import QThread, pyqtSignal

import numpy as np

class TaskWorkerThread(QThread):
    task_running_signal = pyqtSignal(str)
    task_completed_signal = pyqtSignal(str, object)
    all_tasks_finished_signal = pyqtSignal(object) 
    def __init__(self, raw_skeleton_data:np.ndarray, task_list:list):
        super().__init__()
        # self.good_frame = True

        self.raw_skeleton_data = raw_skeleton_data

        #create a dictionary from the task list
        self.tasks = {task_name: {'function': None, 'result': None} for task_name in task_list} 
        # Assign the task functions here
        self.tasks['interpolating']['function'] = self.interpolate_task
        self.tasks['filtering']['function'] = self.filter_task
        self.tasks['finding good frame']['function'] = self.find_good_frame_task
        self.tasks['rotating skeleton']['function'] = self.rotate_skeleton_task
        self.tasks['plotting']['function'] = None

    # def update_worker_settings(self, good_frame:int):
    #     self.good_frame = good_frame  

        # if not run_rotate_skeletons:
        #     self.tasks['rotating skeleton']['function'] = None
        # else:
        #     self.tasks['rotating skeleton']['function'] = self.rotate_skeleton_task


    def run(self):
        for task_info in self.tasks.values(): #clear any previous results 
            task_info['result'] = None

        for task_name, task_info in self.tasks.items():
            if task_info['function'] is not None:
                self.task_running_signal.emit(task_name)
                task_info['result'] = task_info['function']()
                self.task_completed_signal.emit(task_name, task_info['result'])

        self.all_tasks_finished_signal.emit(self.tasks)

    def interpolate_task(self):
        interpolation_values_dict = self.get_all_parameter_values(interpolation_params)
        interpolated_skeleton = interpolate_skeleton_data(self.raw_skeleton_data, method_to_use=interpolation_values_dict['Method'])
        return interpolated_skeleton

    def filter_task(self):
        filter_values_dict = self.get_all_parameter_values(filter_params)
        filtered_skeleton = filter_skeleton_data(self.tasks['interpolating']['result'], order=filter_values_dict['Order'], cutoff=filter_values_dict['Cutoff Frequency'], sampling_rate=filter_values_dict['Sampling Rate'])
        return filtered_skeleton

    def find_good_frame_task(self):
        good_frame_values_dict = self.get_all_parameter_values(good_frame_finder_params)

        if good_frame_values_dict['Auto-find Good Frame']:
            self.good_frame = find_good_frame(self.tasks['filtering']['result'], skeleton_indices=mediapipe_indices, initial_velocity_guess=.5)
            good_frame_finder_params.auto_find_good_frame_param.setValue(False)
            good_frame_finder_params.good_frame_param.setValue(str(self.good_frame))
        else:
            self.good_frame = int(good_frame_values_dict['Good Frame'])
        return self.good_frame

    def rotate_skeleton_task(self):
        rotate_values_dict = self.get_all_parameter_values(rotating_params)
        if rotate_values_dict['Rotate Data:']:
            origin_aligned_skeleton = align_skeleton_with_origin(self.tasks['filtering']['result'], mediapipe_indices, self.good_frame)[0]
        else:
            origin_aligned_skeleton = None
        return origin_aligned_skeleton

    def get_all_parameter_values(self,parameter_object):
        values = {}
        for child in parameter_object.children(): #using this just to access the second level of the parameter tree
            if child.hasChildren():
                for grandchild in child.children():
                    values[grandchild.name()] = grandchild.value()
            else:
                values[child.name()] = child.value()
        return values