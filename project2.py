import pandas as pd
import numpy as np

def main():
	data = pd.read_csv("./data/1_oneHots.csv").iloc[:, 1:]
	
	counts = data.drop('METER', axis=1).groupby(['lat', 'lon', 'WEEKDAY']).sum().reset_index()

	meterCount = data[['lat', 'lon', 'METER']].groupby(['lat', 'lon'])['METER'].nunique().reset_index().rename(columns={'METER': 'meter_count'})

	data = counts.join(meterCount.set_index(['lat', 'lon']), ['lat', 'lon'])
	print(data)

	data.to_csv('./data/2_data.csv')

	# print(data)

if __name__=='__main__':
	main()