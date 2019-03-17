import ResultManager
import csv
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
import threading
import time

class radarObject(object):
	def __init__(self):
		self.dataVector = np.zeros(48)
		self.respRate = 0 
		self.rateMag = 0
		self.timeStamp = "blah"

class OutputObject(object):
	def __init__(self, ofOutput = 0, mbOutput = 0, people = 0):
		self.ofOutput = ofOutput
		self.mbOutput = mbOutput
		self.people = people

if __name__ == '__main__':
	radarData = np.array([])
	ofData = np.array([])
	mbData = np.array([])
	radarLineCount = 0
	ofLineCount = 0
	mbLineCount = 0

	with open('radarTestData.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		radarLineCount = 0
		for row in csv_reader:
			#print(f'{row[0]}')
			radarData = np.append(radarData, row[0]);
			radarLineCount += 1
		print(f'Radar: Processed {radarLineCount} lines.')    
	print(type(radarData))
	radarData = radarData.astype(np.float64)
	#plt.plot(radarData) 
	#plt.title('Radar Data')
	#plt.show()

	with open('ofTestData.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		ofLineCount = 0
		for row in csv_reader:
			#print(f'{row[0]}')
			if(ofLineCount != 0):
				ofData = np.append(ofData, row[1]);
			ofLineCount += 1
		print(f'of: Processed {ofLineCount} lines.')    
	print(type(ofData))
	ofData = ofData.astype(np.float64)
	#plt.plot(ofData) 
	#plt.title('of Data')
	#plt.show()

	with open('mbTestData.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		mbLineCount = 0
		for row in csv_reader:
			#print(f'{row[0]}')
			if(mbLineCount != 0):
				mbData = np.append(mbData, row[1]);
			mbLineCount += 1
		print(f'mb: Processed {mbLineCount} lines.')    
	print(type(mbData))
	mbData = mbData.astype(np.float64)
	#plt.plot(mbData) 
	#plt.title('mb Data')
	#plt.show()

	videoQueue = Queue()
	radarQueue = Queue()
	outputQueue = Queue()
	placeholderQueue = Queue()
	resultManagerObject = ResultManager.ResultManager(placeholderQueue, radarQueue, videoQueue, outputQueue)
	#(self, inputVideoQueue, inputRadarQueue, inputProcessingResultQueue, outputVideoQueue):

	resultManagerObject.start()

	def runRadarQueue():
		dataIndex = 0
		sendIndex = 0
		sendData = np.zeros(48)
		sendObject = radarObject()
		while(1):
			time.sleep(0.25)
			sendIndex = 0
			while sendIndex < 48:
				if(dataIndex>=radarLineCount):
					dataIndex = 0
				sendObject.dataVector[sendIndex] = radarData[dataIndex]
				sendIndex+=1
				dataIndex+=1
			sendObject.timeStamp = "00/00/00 00.00.00"
			sendObject.respRate = 1
			sendObject.respMag = 100

			radarQueue.put(sendObject)

		#	plt.plot(sendObject.dataVector) 
		#	plt.title('Radar Data')
		#	plt.pause(0.05)
		#plt.show()

		return

	def runVideoQueue():
		i =0
		sleepTime= 1/30
		output = OutputObject()
		while(1):
			while(i< ofLineCount-1):
				time.sleep(sleepTime)
				output.ofOutput = ofData[i]
				output.mbOutput = mbData[i]
				output.people = 0

				videoQueue.put(output)
				placeholderQueue.put(1)
				i+=1
			i = 0

		return

	radarT = threading.Thread(target = runRadarQueue, daemon = True)
	radarT.start()
	videoT = threading.Thread(target = runVideoQueue, daemon = True)
	videoT.start()

	plt.clf()	
	plt.close()
	while 1:
		#get shit from output queue
		output = outputQueue.get(True)
		print(output.respRate)
		plt.clf()
		plt.gcf().suptitle(f"Heart Rate = {output.heartRate}  Resp Rate = {output.respRate}  Temp = {output.temp}")
		plt.subplot(3,1,1)		#plot mb data
		plt.plot(output.mbData) 
		plt.title('mb Data')
		plt.gca().set_ylim([-2,2])
		plt.subplot(3,1,2)		#plot of data
		plt.plot(output.ofData) 
		plt.title('of Data')
		plt.gca().set_ylim([-2,2])
		plt.subplot(3,1,3)		#plot radar data
		plt.plot(output.radarData) 
		plt.title('Radar Data')
		plt.gca().set_ylim([-2,2])
		plt.pause(0.05)

	plt.show()