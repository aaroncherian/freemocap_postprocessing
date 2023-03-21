# import nbformat

# nb = nbformat.read('notebook_text.py', 
#                    nbformat.current_nbformat)

# nbformat.write(nb, 'notebook_test.ipynb', 
#                nbformat.NO_CONVERT)
# # conv = convert.read(open('source.py', 'r'), 'py')
# # convert.write(conv, open('source.ipynb', 'w'), 'ipynb')

import papermill as pm
# from pathlib import Path
# import papermill as pm

#pm.execute_notebook('com_timeseries_plotter.ipynb', 'com_timeseries_plotter_output.ipynb', parameters = {'path_to_session':r'C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-03-20_13_58_15\recording_14_06_10_gmt-4'})
# x = pm.inspect_notebook('simple_notebook.ipynb')

# name = r'C:/users'
# res = pm.execute_notebook(
#     'simple_notebook.ipynb',
#     'simple_notebook_output.ipynb',
#     parameters = dict(name=name)
# )

path_to_session = r'C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-03-20_13_58_15\recording_14_06_10_gmt-4'

res = pm.execute_notebook(
    'com_timeseries_plotter.ipynb',
    'com_timeseries_plotter_output.ipynb',
    parameters = dict(path_to_session=path_to_session)
)

f = 2