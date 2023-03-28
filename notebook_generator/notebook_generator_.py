import papermill as pm

path_to_session = r'C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-01-17_15_47_19\15_50_24_gmt-5'

res = pm.execute_notebook(
    'com_timeseries_plotter.ipynb',
    'com_timeseries_plotter_output.ipynb',
    parameters = dict(path_to_session=path_to_session)
)

f = 2