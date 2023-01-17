
##For the demo (1/18/23)
1) Run 'skeleton_visualization_gui.py' to bring up a window with just the frame slider widget and the skeleton view widget - you can use it to load in a recording
and scroll through the data
2) 'zero_crossing_calculator_and_plotter.py' will save out both a numpy and a CSV file with the frame *before* a zero crossing occurred - the second column represents
    the slope of that line. 
    - You can change the joint that's being plotted, the direction of motion plotted, and the threshold to ignore subsequent crossings at the start of the script
    - The start and end frames, when set to None, will be default plot and save out zero crossings for the whole recording. You can adjust these if you want to 
      just get the data for a specific frame interval 


2) Run 'skeleton_multi_cam_visualization.py' to bring up a window with the skeleton visualization that also lets you load a folder of videos alongside the skeleton visualization
3) The freemocap_utils.GUI_widgets folder contains the widgets for the slider (slider_widget.py), the skeleton visualizer (skeleton_view_widget.py), 
the multi camera display (multi_camera_display.py), and a single camera display (single_camera_display.py)
4) The freemocap_utils.mediapipe_skeleton_builder.py file is used to construct the skeleton visualization that appears in the GUI
5) The gui_vis_missing_limbs.py and GUI_vis_with_repro_error.py files are older GUI versions that aren't updated to import/work with widgets, but are potential references
for trying to provide useful data to someone trying to analyze their session - the first file shows plots of the number of missng limbs throughout the session, and the second
plots reprojection error with regard to certain limbs