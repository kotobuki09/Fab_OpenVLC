import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

url = "https://raw.githubusercontent.com/kotobuki09/Fab_OpenVLC/main/Dopper_2302.csv?token=GHSAT0AAAAAACFWXAL5QHUFUL2J7TG24HIYZHOCO3A"

missing_values = ["NM"]
df = pd.read_csv(url, na_values = missing_values)
df.drop(columns=df.columns[0], axis=1,inplace=True)
df = df.apply(lambda x: x.fillna(x.mean()))

y = df["Doppler"]
x = np.linspace(0, 120, 601)

df['Time'] = x

# Use a continuous color palette for better visualization
cmap = plt.get_cmap('coolwarm')
norm = plt.Normalize(df['Doppler'].min(), df['Doppler'].max())
colors = cmap(norm(df['Doppler'].values))

fig, ax = plt.subplots()
sns.barplot(x=df["Time"], y=df["Doppler"], palette=colors, ax=ax)
xticks = [i for i in range(0, 121, 20)]
plt.xticks([i*5 for i in xticks], xticks)

plt.xlabel('Time(s)')
plt.ylabel('Doppler Velocity')
plt.margins(x=0)
plt.margins(y=0)

plt.show()
fig.savefig("Doppler_velocity_colors.png", transparent=True, bbox_inches='tight', pad_inches=0.2)
