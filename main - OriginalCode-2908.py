#Import pandas, numpy and matplotlib library
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Save database URL to url
#url = "https://raw.githubusercontent.com/kotobuki09/TrackLocation/master/icontrol_data.csv"
#url = "https://raw.githubusercontent.com/kotobuki09/kngo/main/Dopper_2302.csv"
url = "https://raw.githubusercontent.com/kotobuki09/Fab_OpenVLC/main/Dopper_2302.csv?token=GHSAT0AAAAAACFWXAL4PKZAONDAPKDMY2Y6ZHNZH4Q"



# Creating a DataFrame with dataset and change all the "NM" value to missing value
missing_values = ["NM"]
df = pd.read_csv(url, na_values = missing_values)
#Drop first column
#df.drop(columns=df.columns[[0,1]], axis=1,inplace=True) #delete 2 column 0, and 1
df.drop(columns=df.columns[0], axis=1,inplace=True)
# Replace all the missing value using median
df = df.apply(lambda x: x.fillna(x.mean()))


print(df.head)
#print(df.columns[:3])
#print(df.Location.unique()+1)

#Draw the new graph for the Doppler Velocity performance
#y= df.iloc[:,:1].values
#y= np.squeeze(y)
#y=list(y)
y=df["Doppler"]

#print(x)
#x = []
#for i in range(0, 604):
#    x.append(i * 0.2)
x=np.linspace(0, 120, 601)
values = [i/5 for i in range(0, 601)]

# Create a range of time values from 0s to 120s with 0.2s increments
#x = pd.date_range(start='00:00:00', end='00:02:00', freq='200ms')

# Create a DataFrame with the time values
#dftime = pd.DataFrame({'Time': x})

# Print the first few rows of the DataFrame
#print(df.head())




#print(y)
#plt.plot(x, y)
#plt.title('Doppler velocity extracted from testbed scenario')
#plt.xlabel('Time(s)')
#plt.ylabel('Doppler velocity')
#plt.show()

#df2 = pd.DataFrame (x, columns = ['Time'])
#print(df2.head)

df['Time'] = x
print(df.head)
print(type(df))

import seaborn as sns
import pandas as pd

import numpy as np
import matplotlib


#use red for bars with value less than 10 and green for all other bars

#cols = ['red' if y < 2 else 'green' for y in df.Doppler]
cols = ['green' if y < 3 else 'blue' if 3 <= y < 7 else 'red' for y in df.Doppler]
x=df["Time"]
y=df["Doppler"]
fig=sns.barplot(x=x, y=y,palette=cols)
xticks = [i for i in range(0, 121, 20)]
plt.xticks([i*5 for i in xticks], xticks)
#ticks = plt.xticks(x[::400], df['Time'].values[::400], rotation=90)
#plt.xticks(range(len(df["Time"])), df["Time"])


# Set the axis labels and title
plt.xlabel('Time(s)')
plt.ylabel('Doppler Velocity')
plt.margins(x=0)
plt.margins(y=0)
# Show the plot
plt.show()

fig.figure.savefig("Doppler062023.png",transparent = True, bbox_inches = 'tight', pad_inches = 0.2)