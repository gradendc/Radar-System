import numpy as np
import matplotlib.pyplot as plt
import time, math
import jade
import csv
import time
import numpy.fft as fft
from scipy.signal import savgol_filter

# plt.clf()	#clear any shit on plots??
# plt.close()
#test = np.arange(0, 10, 1)
#plt.plot(test)
#plt.show()

radar_data = np.array([]).astype(np.float64)
video_data = np.array([]).astype(np.float64)

#get radar data
with open('L_25Hz_run2.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	for row in csv_reader:
		#print(f'{row[0]}')
		if line_count >= 580:
			radar_data = np.append(radar_data, row[0]);
		line_count += 1
	print(f'Processed {line_count} lines.')    
print(type(radar_data))
radar_data = radar_data.astype(np.float64)
plt.subplot(2, 2, 1)
plt.plot(radar_data) 
plt.title('Radar Data')
#plt.show()

#TODO: truncate to 10 seconds of data
#want 1920 points

#get video data
with open('Ltest2.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	for row in csv_reader:
		#print(f'{row[0]}')
		if line_count != 0:
			video_data = np.append(video_data, row[1]);
		line_count += 1
	print(f'Processed {line_count} lines.') 
print(video_data)
video_data = video_data.astype(np.float64)
#plt.subplot(2, 2, 2)
#plt.plot(video_data) 
#plt.title('video data')
#plt.show()



radar_data = radar_data.astype(np.float64)
video_data = video_data.astype(np.float64)
L = len(radar_data);
L2 = len(video_data);
print(L)
print(L2)
#plt.plot(radar_data) 
#plt.title('radar data')
#plt.show()

#TODO make sure that arrays start at same physical time so they can correlate properly

#normalize y axis of data
radar_mean = np.mean(radar_data)
radar_sd = np.std(radar_data)
radar_data = (radar_data - radar_mean)/radar_sd
video_mean = np.mean(video_data)
video_sd = np.std(video_data)
video_data = (video_data - video_mean)/video_sd
#plt.plot(video_data) 
#plt.title('normalized data')
#plt.show()

#interpolate video data
radar_sampleHz = 48/0.25
#radar_time = np.arange(0, ( float(L)/float(radar_sampleHz) ), (1/float(radar_sampleHz)) )
radar_time = np.arange(0, L, 1)
radar_time = radar_time/radar_sampleHz
#print(radar_time)
#print("timevec", len(radar_time))
#print(radar_time)
#plt.plot(radar_time, radar_data) 
#plt.show()
video_sampleHz = 30
#video_time = np.arange(0, (L2/video_sampleHz), (1/video_sampleHz))
video_time = np.arange(0, L2, 1)
video_time = video_time/video_sampleHz
#plt.plot(video_time, video_data) 
#plt.show()
video_data = np.interp(radar_time.astype(np.float64), video_time.astype(np.float64), video_data.astype(np.float64))
plt.subplot(2, 2, 2)
plt.plot(video_data) 
plt.title('Video Data (interpolated to radar time)')
#plt.show()
##processed = np.append(radar_data, video_data, axis=0)
processed = np.vstack((radar_data,video_data))
processed = processed.astype(np.float64)
print(processed)
#processed = np.ndarray(shape=(2, L), buffer=np.array(self.ica_data_buffer))

#Do JADE ICA
#processed = self.normalize_matrix(processed)
ICA = jade.main(processed)
#print(ICA)
plt.subplot(2, 2, 3)
plt.plot(ICA[:, 0]) 
plt.title("ICA Output")
#plt.show()
#plt.plot(ICA[:, 1]) 
#plt.show()
firstComponent = np.asarray(ICA[:, 0]).astype(np.float64)
#print(firstComponent.shape)
firstComponent = np.squeeze(firstComponent)
#print(firstComponent.shape)
print("first component: ", firstComponent)

#FFT processing on firstComponent
#TODO: possibly share FFT processing fxn with ofProcessing?
n = 4096 	#ICA length should = length of radar data buffer = 1000?
icaFFT = fft.fft(firstComponent, n=n)
#icaFFT = fft.fft(video_data, n=n)
print(type(icaFFT))
icaFFT = np.absolute(icaFFT)
#assume Fs is the same as radar Fs??? = chirps/frame * frames/second = chirps/second = 48*4 = 192
Fs = 192
freqAxis = fft.fftfreq(n, d=1/Fs)
lowerCutOff=int(0.1/(Fs/n))		#0.1Hz
upperCutOff=int(3/(Fs/n))		#3 Hz	
freqAxis=freqAxis[lowerCutOff:upperCutOff]
icaFFT=icaFFT[lowerCutOff:upperCutOff]
print("FFT", icaFFT)
maxIndex = np.argmax(icaFFT)
#maxFreq = maxIndex*(Fs/n)	
maxFreq = freqAxis[maxIndex]	
print("max freq = ", maxFreq)
plt.subplot(2, 2, 4)
#plt.plot(freqAxis, icaFFT) 
#plt.title(f"FFT, RR = {maxFreq}")
#plt.show()

def processForDisplay(inputData, smoothWindow , smoothPolyOrder = 3, detrendPolyOrder = 3):
	data = inputData 	#make copy b/c idk if python functions are pass by value or pass by reference
	#process data for displaying to user
	#smoothPolyOrder must be an odd number

	#normalize signal to SD
	#mean = np.mean(data)
	#sd = np.std(data)
	#data = (data - mean)/sd

	#detrending
	L = len(data)
	x = np.arange(0, L, 1)
	model = np.polyfit(x, data, detrendPolyOrder)
	predicted = np.polyval(model, x)
	data = data - predicted

	#smooth signal
	processedData = savgol_filter(data, 101, 3)

	

	return processedData

dVideo = processForDisplay(radar_data, 101, 3, 4)
plt.subplot(2, 2, 4)
plt.plot(dVideo) 
plt.title("processed data")
plt.show()