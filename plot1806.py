# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Define data URL
url = "https://raw.githubusercontent.com/kotobuki09/Fab_OpenVLC/main/Dopper_1806.csv?token=GHSAT0AAAAAACCS5Q76SJ4K5Z2ZSAH2ITCAZEO3KDQ"

# Read the data into a DataFrame, handling missing values
missing_values = ["NM"]
df = pd.read_csv(url, na_values=missing_values)
df.drop(columns=df.columns[0], axis=1, inplace=True)
df = df.apply(lambda x: x.fillna(x.mean()))

# Prepare data for plotting
y = df["Doppler"]
x = np.linspace(0, 120, 601)
df['Time'] = x

# Generate continuous color map using "cividis" from Matplotlib
color_map = plt.cm.get_cmap("inferno")
norm = plt.Normalize(df['Doppler'].min(), df['Doppler'].max())
colors = color_map(norm(df['Doppler']))

# Create the plot
fig, ax = plt.subplots()
sns.barplot(x=df["Time"], y=df["Doppler"], palette=colors, ax=ax, width=0.9)

# Customize plot appearance
xticks = [i for i in range(0, 121, 20)]
plt.xticks([i*5 for i in xticks], xticks)
ax.set_xlabel('Time(s)')
ax.set_ylabel('Doppler Velocity')
plt.margins(x=0)
plt.margins(y=0)

# Show and save the plot
plt.show()
fig.savefig("Doppler062023v5.png", transparent=True, bbox_inches='tight', pad_inches=0.2)
