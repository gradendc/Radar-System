from multiprocessing import Process, Queue
import sys
import numpy
import numpy.fft as fft
#import cv2
import jade
from scipy.signal import savgol_filter

import matplotlib.pyplot as plt


class OutputVitals(object):
	def __init__(self, respRate, heartRate, temp, radarBufSize, ofBufSize, mbBufSize):
		self.respRate = respRate
		self.heartRate = heartRate
		self.temp = temp

		self.ofData = numpy.zeros(ofBufSize)
		self.mbData = numpy.zeros(mbBufSize)
		self.radarData = numpy.zeros(radarBufSize)

"""
Manages and saves past peoples data 
matches reapearing people
streams live people with their results
outputs stored people
"""
class ResultManager(Process):
	def __init__(self, inputVideoQueue, inputRadarQueue, inputProcessingResultQueue, outputVideoQueue):
		self.outputVideo = outputVideoQueue
		self.data = inputProcessingResultQueue
		self.inputVideo = inputVideoQueue

		#data processing buffers
		self.radarBufSize = 1000
		self.ofBufSize = 1000
		self.mbBufSize = 1000
		self.radarBuffer = numpy.zeros(self.radarBufSize)
		self.ofBuffer = numpy.zeros(self.ofBufSize)
		self.mbBuffer = numpy.zeros(self.mbBufSize)

		#store other radar queue outputs
		self.radarRR = 0
		self.radarRRMag = 0
		self.radarTimeStamp = "placeholder"

		#store previous respiratory rate
		self.prevRR = 0 

		#output object
		self.outputVitalSigns = OutputVitals(0, 0, 0, self.radarBufSize, self.ofBufSize, self.mbBufSize)

		super(ResultManager, self).__init__()

		#TODO test with actual radar server data
		#self.radarDataQueue = Queue()
		#self.RadarServer = rs.RadarServer(self.radarDataQueue)
		#self.RadarServer.start()
		self.radarDataQueue = inputRadarQueue

		# TODO what happens if queue overfills? does it block process, or overwrite data, etc...
		# TODO get radar Data here

	def run(self):
		print("ResultManager Starting up")
		count = 0
		#synchronization variables:
		radarMax = 2
		videoMax = 15
		radarCounter = 0
		videoCounter = 0
		radarReset = False
		videoReset = False
		newDataFlag = False

		while True:  # change to what is done in process manager
			
			#code that makes queues non-blocking for each other. if a queue is empty, the stored data will remain unchanged
			# if(!self.data.empty() && !self.inputVideo.empty()):
			# 	frame = self.inputVideo.get(True)
			# 	resultData = self.data.get(True)
			# 	self.storeResultData(resultData)
			# if(!self.radarDateQueue.empty()):
			# 	radarData = self.radarDataQueue.get(True)
			# 	self.storeRadarData(radarData)

			#synchronization code:
			#radar and video queues "block" each other until they have each updated their max times
			#if one of the queues is "blocked", the data will remain unchanged from the previous loop

			#want to block on videoQueue, so only check if videoCounter<vidMax 
			#if( (videoCounter<videoMax) and (not self.data.empty()) and (not self.inputVideo.empty()) ):
			if(videoCounter<videoMax):
				#update video buffer
				frame = self.inputVideo.get(True)
				resultData = self.data.get(True)
				self.storeResultData(resultData)
				videoCounter+=1
				if(videoCounter == videoMax):
					#have updated the max amount, need to "block" until radar catches up
					videoReset = True
				newDataFlag = True

			if( (radarCounter<radarMax) and (not self.radarDataQueue.empty()) ):
				#update radar data
				radarData = self.radarDataQueue.get(True)
				self.storeRadarData(radarData)
				radarCounter+=1
				if(radarCounter == radarMax):
					#have updated the max amount, need to "block" until video catches up
					radarReset = True
				newDataFlag = True
			if(videoReset and radarReset):
				videoReset = False
				radarReset = False
				videoCounter = 0
				radarCounter = 0
			#Do processing if have new data:
			if(newDataFlag):
				newDataFlag = False

				self.outputVitalSigns.heartRate = self.mbProcessing()

				ofRespRate, ofRRMag = self.ofProcessing()
				ICARespRate = self.ICAProcessing()
				outlierThresh = 1; 		#SD of resp rates: units in Hertz
				self.outputVitalSigns.respRate = self.analyzeRespRate(self.radarRR, self.radarRRMag, ICARespRate, ofRespRate, ofRRMag, outlierThresh)

				self.outputVitalSigns.temp = 0		#placeholder for IR camera stuff

				self.outputVitalSigns.ofData = self.processForDisplay(self.ofBuffer, smoothWindow = 51)
				self.outputVitalSigns.mbData = self.processForDisplay(self.mbBuffer)
				self.outputVitalSigns.radarData = self.processForDisplay(self.radarBuffer)
				self.outputVideo.put(self.outputVitalSigns)
				#TODO: for output data buffers, include time axis??
			
			#Laurenz's Code: 
			#self.outputVideo.put(drawBreathingTriangle(resultData.people, resultData.ofOutput, frame))
			# print(count)
			# testing code:
			#cv2.imwrite("/Users/laurenzschmielau/Desktop/CPEN491/Vitalie/OPTestData/V1_TestOutputImages/V1_frame%d.jpg" % count, self.outputVideo.get(True))
			#count += 1

			



	def storeResultData(self, inputData):
		# input - "frame" of data from inputProcessingResultQueue
		# function adds frame to circular buffer for HR and video RR processing
		
		self.ofBuffer = numpy.roll(self.ofBuffer,-1)
		self.ofBuffer[self.ofBufSize - 1] = inputData.ofOutput 
		
		self.mbBuffer = numpy.roll(self.mbBuffer,-1)
		self.mbBuffer[self.mbBufSize - 1] = inputData.mbOutput

		return

	def storeRadarData(self, inputRadarData):
		# store radar data into buffer
		# store other radar datas from matlab

		# class radarObject(object):
		# 		def __init__(self, ofOutput, mbOutput, people):
		# 		self.dataVector 
		# 		self.respRate 
		# 		self.rateMag
		# 		self.timeStamp

		chirpsPerFrame = len(inputRadarData.dataVector)		#should be 48
		self.radarBuffer = numpy.roll(self.radarBuffer,-chirpsPerFrame)
		self.radarBuffer[ (self.radarBufSize-chirpsPerFrame):] = inputRadarData.dataVector; 

		self.radarRR = inputRadarData.respRate
		self.radarRRMag = inputRadarData.rateMag
		self.radarTimeStamp = inputRadarData.timeStamp

		return 

	def mbProcessing(self):
		# do heart rate microblushing processing
		# maybe we can just do processing independantly, like the radar matlab stuff
		# and just pull the calculated frequency
		heartRate = 1

		return heartRate

	def ofProcessing(self):
		# do openflow respiratory rate processing
		# return calculated RR and normalized magnitude of the FFT at the RR frequency

		motion  = self.ofBuffer
		Fs = 30
		of_n = 4096

		#process FFT
		spectrum = fft.fft(motion,n=of_n)
		spectrum=abs(spectrum)
		mean = numpy.mean(spectrum)
		sd = numpy.std(spectrum)
		freq = fft.fftfreq(len(spectrum),d=1/Fs)
		lowerCutOff = int(0.2/(Fs/of_n))
		upperCutOff = int(3/(Fs/of_n))
		freq=freq[lowerCutOff:upperCutOff]
		spectrum=spectrum[lowerCutOff:upperCutOff]

		#detect peak
		#c = (numpy.diff(numpy.sign(numpy.diff(spectrum))) < 0).nonzero()[0] + 1 # local max
		#toppeak=max(spectrum[c])
		#for x in c:
		#	if(toppeak==spectrum[x]):
		#		break
		#respRate=abs(freq[x])
		#TODO: note for fonda, why not do this for peak detection? your code cant handle if there are no peaks for some reasn
		maxIndex = numpy.argmax(spectrum)
		respRate = freq[maxIndex]

		#calculate normalized magnitude of peak
		#TODO: need to take into acount that 
		#      1)different lengths and 2)different filtering (cut off freq)
		#      will affect FFT normalization between radar and video. 
		#      need to deal with this
		#peakVal = spectrum[x]
		peakVal = spectrum[maxIndex]
		normMagnitude = (peakVal - mean)/sd

		return respRate, normMagnitude

	def ICAProcessing(self):
		#do ICA processing

		#TODO: need way to make sure that radar and video data are time syncronized 
		#      meaning that the data sequence starts at the same time (or else ICA wont work)
		#      maybe can take advantage of interpolation code?

		#Normalize radar and video data to their respective standard deviations
		#if SD=0, don't divide by sd (or will get NaNs)
		radarSD = numpy.std(self.radarBuffer)
		if(radarSD == 0):
			normRadarBuffer = self.radarBuffer - numpy.mean(self.radarBuffer)
		else:
			#radar_mean = np.mean(radar_data)
			#radar_sd = np.std(radar_data)
			normRadarBuffer = (self.radarBuffer - numpy.mean(self.radarBuffer) )/radarSD
		ofSD = numpy.std(self.ofBuffer)
		if(ofSD == 0):
			normOFBuffer = self.ofBuffer - numpy.mean(self.ofBuffer)
		else:
			#video_mean = np.mean(video_data)
			#video_sd = np.std(video_data)
			normOFBuffer = (self.ofBuffer - numpy.mean(self.ofBuffer) )/ofSD

		normRadarBuffer = normRadarBuffer.astype(numpy.float64)
		normOFBuffer = normOFBuffer.astype(numpy.float64)

		#Interpolate video data to same sample rate/timescale as radar data
		radarSampleHz = 48/0.25
		#radarTime = numpy.arange(0, (self.radarBufSize/radarSampleHz), (1/radarSampleHz))
		radarTime = numpy.arange(0, self.radarBufSize, 1)
		radarTime = radarTime/radarSampleHz
		#print("timevec", len(radar_time))
		ofSampleHz = 30 		#TODO replace with actual value
		#ofTime = numpy.arange(0, (self.ofBufSize/ofSampleHz), (1/ofSampleHz))
		ofTime = numpy.arange(0, self.ofBufSize, 1)
		ofTime = ofTime/ofSampleHz
		normOFBuffer = numpy.interp(radarTime, ofTime, normOFBuffer)

		if len(normRadarBuffer) != len(normOFBuffer):
			print("Error: radarBuffer size does not match ofBuffer size.")
			return

		jadeInput = numpy.vstack((normRadarBuffer,normOFBuffer))
		jadeInput = jadeInput.astype(numpy.float64)

		#Do JADE ICA
		ICA = jade.main(jadeInput)
		firstComponent = ICA[:, 0];
		secondComponent = ICA[:, 1];
		#Possibly collect/analyze more ICA components? (right now only outputs 2, first is strongest)

		#FFT processing on firstComponent
		#TODO: possibly share FFT processing fxn with ofProcessing?
		firstComponent = numpy.asarray(ICA[:, 0]).astype(numpy.float64)
		firstComponent = numpy.squeeze(firstComponent)
		ica_n = 4096 
		icaFFT = fft.fft(firstComponent, n=ica_n)
		icaFFT = numpy.absolute(icaFFT)
		#assume Fs is the same as radar Fs??? = chirps/frame * frames/second = chirps/second = 48*4 = 192
		RadarFs = 192
		freqAxis = fft.fftfreq(ica_n, d=1/RadarFs)
		lowerCutOff=int(0.1/(RadarFs/ica_n))		#0.1Hz
		upperCutOff=int(3/(RadarFs/ica_n))		#3 Hz	
		freqAxis=freqAxis[lowerCutOff:upperCutOff]
		icaFFT=icaFFT[lowerCutOff:upperCutOff]
		maxIndex = numpy.argmax(icaFFT)
		#maxFreq = maxIndex*(RadarFs/ica_n)	
		maxFreq = freqAxis[maxIndex]

		return maxFreq

	def analyzeRespRate(self, radarRR, radarMag, icaRR, ofRR, ofMag, outlierThresh):
		#right now, simply calculates mean and SD of 3 RRs
		#if SD is above outlierThresh, that means that there is discrepancy
		#with calculations, so just use previous respiratory rate

		RRarr = numpy.array([radarRR, icaRR, ofRR])
		mean = numpy.mean(RRarr)
		sd = numpy.std(RRarr)

		if sd < outlierThresh:
			self.prevRR = mean
			return mean
		else:
			return self.prevRR
			# or (for method below):
			# if radarMag > ofMag:
			# 	return radarRR
			# else:
			# 	return ofMag

		#idea for more robust detection: n
		#in other functions calculate magnitude or "strength"
		#        of detected frequency along frequency (i.e. magnitude on fft)
		#Normalize the magnitudes with the s.d. of the FFTs
		#then, when get the 3RRs in this function, do the current method, except if SD is above
		#the outlierThresh, then use the radar or video RR with the highest power

	def processForDisplay(self, inputData, smoothWindow= 101, smoothPolyOrder = 3, detrendPolyOrder = 3):
		#process data for displaying to user
		#smoothPolyOrder must be an odd number
		data = inputData 	#make copy b/c idk if python functions are pass by value or pass by reference

		#normalize signal to SD
		mean = numpy.mean(data)
		sd = numpy.std(data)
		if(sd==0):				#can't divide by zero
			data = data-mean
		else:
			data = (data - mean)/sd

		#detrending
		L = len(data)
		x = numpy.arange(0, L, 1)
		model = numpy.polyfit(x, data, detrendPolyOrder)
		predicted = numpy.polyval(model, x)
		data = data - predicted

		#smooth signal
		processedData = savgol_filter(data, smoothWindow, smoothPolyOrder)

		return processedData


def drawBreathingTriangle(people, ofOutput, frame):
	for val in ofOutput:
		person = people.pop(0)
		if val > 0:
			x1 = person.right_shoulder_x
			y1 = person.mid_hip_y
			x2 = person.left_shoulder_x
			y2 = person.mid_hip_y
			x3 = person.mid_hip_x
			y3 = person.right_shoulder_y
			# up
		else:
			x1 = person.right_shoulder_x
			y1 = person.right_shoulder_y
			x2 = person.left_shoulder_x
			y2 = person.right_shoulder_y
			x3 = person.mid_hip_x
			y3 = person.mid_hip_y
			# down
		pts = numpy.array([[x1, y1], [x2, y2], [x3, y3]], numpy.int32)
		cv2.polylines(frame, [pts], True, (0, 230, 0), 10)
	return frame













