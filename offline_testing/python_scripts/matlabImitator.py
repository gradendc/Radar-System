#This is script is for the purpose of testing the integrated system if you don't have Matlab installed
#Instead of starting Matlab and running the Matlab script, just run this script
#
#This script will stream a 10 second loop of "phase point" data and placeholder Timestamp, 
#      RespRate, and RateMag values in an endless loop 
#It will use the dataLogger script and should communicate with the server in the same way 
#      as the Matlab script would

import csv
import numpy as np
import matplotlib.pyplot as plt
import dataLogger2 
import time

chirps_per_frame =48
sendData = np.zeros(chirps_per_frame)
radarData = np.array([]).astype(np.float64)

with open('fakeDataForMatlabImitator.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	for row in csv_reader:
		#print(f'{row[0]}')
		radarData = np.append(radarData, row[0]);
		line_count += 1
	print(f'Processed {line_count} lines.')    
print(type(radarData))
radarData = radarData.astype(np.float64)
plt.plot(radarData) 
plt.title('Radar Data')
plt.show()

dataIndex = 0
sendIndex = 0

plt.clf()	#clear any shit on plots??
plt.close()
#collectData = np.array([])
while(1):
	time.sleep(0.25)
	sendIndex = 0
	while sendIndex < 48:
		if(dataIndex>=line_count):
			dataIndex = 0
		sendData[sendIndex] = radarData[dataIndex]
		sendIndex+=1
		dataIndex+=1
	timeStamp = "19/04/03 00:00:00"
	respRate = 1
	respMag = 100
	dataLogger2.sendData(timeStamp, respRate, respMag, sendData)

	#collectData =np.append(collectData, sendData)
	#plt.plot(collectData) 
	#plt.title('Radar Data')
	#plt.gca().set_ylim([-0.2,1.2])
	
	#plt.pause(0.05)
#plt.show()