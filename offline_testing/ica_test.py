import numpy as np
import matplotlib.pyplot as plt
import time, math
import jade
import csv
import time

radar_data = np.array([])
video_data = np.array([])
with open('data_log.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	line_count = 0
	for row in csv_reader:
		#print(f'{row[0]}')
		line_count += 1
		if line_count <= 2916:
			radar_data = np.append(radar_data, row[0]);
		if line_count > 2916 :
			video_data = np.append(video_data, row[0]);
			#video_data.append(row[0]);
	print(f'Processed {line_count} lines.')    
plt.plot(radar_data) 
plt.show()

#TODO will need to interpolate? (or something) data so that the time points/sample rate are the same
#TODO and also make sure that arrays start at same physical time so they can correlate properly
L = len(radar_data);
L2 = len(video_data);
print(L)
print(L2)
#processed = np.append(radar_data, video_data, axis=0)
processed = np.vstack((radar_data,video_data))
processed = processed.astype(np.float64)
print(processed)
#processed = np.ndarray(shape=(2, L), buffer=np.array(self.ica_data_buffer))

#Do JADE ICA
#processed = self.normalize_matrix(processed)
ICA = jade.main(processed)
print(ICA)
plt.plot(ICA[:, 0]) 
plt.show()
plt.plot(ICA[:, 1]) 
plt.show()

#parsedICADict = self.parse_ICA_results(ICA, L)
#resultDict = self.extractFrequency(L, parsedICADict["array"], 25)
#self.bpm = resultDict["freq_in_hertz"] * 60

