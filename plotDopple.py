#Import pandas, numpy and matplotlib library
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

#Save database URL to url  
#url = "https://raw.githubusercontent.com/kotobuki09/TrackLocation/master/icontrol_data.csv"
url = "https://raw.githubusercontent.com/kotobuki09/Fab_OpenVLC/main/Dopper_2302.csv?token=GHSAT0AAAAAAB6XFZLN23ECBD4ZALOBOLXCY7YXKLA"


# Creating a DataFrame with dataset and change all the "NM" value to missing value 
missing_values = ["NM"]
df = pd.read_csv(url, na_values = missing_values)
#Drop first column
#df.drop(columns=df.columns[[0,1]], axis=1,inplace=True) #delete 2 column 0, and 1
df.drop(columns=df.columns[0], axis=1,inplace=True)
# Replace all the missing value using median 
df = df.apply(lambda x: x.fillna(x.mean()))

#Print the first 5 values of the dataframe
print(df.head)
#print(df.columns[:3])
#print(df.Location.unique()+1)

