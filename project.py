import pandas as pd
import numpy as np
import json
import re
import string
import ast
from datetime import datetime, timedelta

def parseJson(jason):
    m = json.loads(jason)['coordinates']
    return m[0], m[1]

def roundToGrid(n):
	# A difference of 0.0005 in latitude/longitude in Downtown Vancouver corresponds to around a 130m distance in that direction
	# So this returns the center of these arbitrary grid squares that the meter is located in
	return 0.0005 * round(n / 0.0005)

def elapsedTime(startTime, elapsedMinutes):
	d = timedelta(minutes=elapsedMinutes)
	return startTime + d

def toOneHot(row):
	for h in row[3]:
		row[5 + h] = 1


def main():
	parkingMeters_df = pd.read_csv("./data/parking-meters.csv", ";", dtype = {'PAY_PHONE': str, 'Geom': str}, usecols = ["PAY_PHONE", "Geom"])
	parkingMeters_df['lat'], parkingMeters_df['lon'] = zip(*parkingMeters_df['Geom'].map(parseJson))
	payByPhone_df= pd.read_csv("./data/pay-by-phone-parking-august-1-to-26-2017.csv", ";", 
		dtype = {'METER': str, 'MINUTES': str}, 
		usecols = ["METER", "DATE START", "MINUTES"],
		low_memory=False)
	payByPhone_df2= pd.read_csv("./data/no-name1.csv", ";",
		dtype = {'METER': str, 'MINUTES': str},
		usecols=["METER", "DATE START", "MINUTES"])
	payByPhone_df = pd.concat([payByPhone_df, payByPhone_df2])
	data = payByPhone_df.join(parkingMeters_df.set_index("PAY_PHONE"), 'METER').dropna()
	data = data[data.MINUTES.apply(lambda x: x.isnumeric())]
	data['MINUTES'] = pd.to_numeric(data['MINUTES'])

	# FOR DEV, SO WE DON'T WAIT AN HOUR PER ATTEMPT
	# data = data.head(1000)


	data["DATE START"] = pd.to_datetime(data["DATE START"])
	data["DATE START"] = data["DATE START"].map(lambda x: x.replace(second = 0))
	data["DATE END"] = data.apply(lambda x: elapsedTime(x["DATE START"], x['MINUTES']), axis=1)
	data["START HOUR"] = data["DATE START"].map(lambda x: x.hour)
	data["END HOUR"] = data["DATE END"].map(lambda x: x.hour)
	data['HOURS'] = [[hour for hour in range(1, 24) if t[0] <= hour and hour <= t[1]] for t in zip(data['START HOUR'], data['END HOUR'])]
	data["WEEKDAY"] = data["DATE START"].map(lambda x: x.weekday())
	data['lat'] = roundToGrid(data['lat'])
	data['lon'] = roundToGrid(data['lon'])
	data = data.drop(['Geom', 'DATE START', 'DATE END', 'MINUTES', 'START HOUR', 'END HOUR'], 1)

	for i in range(0, 24):
		data[str(i)] = 0

	dlist = data.values.tolist()
	for r in dlist:
		toOneHot(r)

	data2 = pd.DataFrame(dlist, columns=list(data.columns))
	data2 = data2.drop('HOURS', 1)
	data2.to_csv("./data/1.onehots")
	# print(data2)


if __name__=='__main__':
	main()