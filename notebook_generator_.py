
path_to_session = r'C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-03-20_13_58_15\recording_14_06_10_gmt-4'

res = pm.execute_notebook(
    'com_timeseries_plotter.ipynb',
    'com_timeseries_plotter_output.ipynb',
    parameters = dict(path_to_session=path_to_session)
)

f = 