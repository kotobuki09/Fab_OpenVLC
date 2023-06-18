
#import pandas as pd
#df = pd.read_csv('E:\\Fab_OpenVLC\\ControlUnit\\file2.csv')
#df.head()


import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv('E:\\Fab_OpenVLC\\ControlUnit\\file2.csv',index_col=0)
#data = data.head()

#df = pd.DataFrame(data, columns=["Time (s)","Max_RSSI_VLC","Min_RSSI_VLC","Std_RSSI_VLC", "link_quality_wifi","signal_level_wifi","noise_level_wifi"])
df = pd.DataFrame(data, columns=["Time (s)","Std_RSSI_VLC", "link_quality_wifi","signal_level_wifi","noise_level_wifi"])

# plot the dataframe
#df.plot(x="Time (s)", y=["Max_RSSI_VLC","Min_RSSI_VLC","Std_RSSI_VLC", "link_quality_wifi","signal_level_wifi","noise_level_wifi"])
df.plot(x="Time (s)", y=["Std_RSSI_VLC", "link_quality_wifi","signal_level_wifi","noise_level_wifi"])
#plt.xlim(left = 1, right = 100)
plt.show()


