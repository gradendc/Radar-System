import csv
import subprocess
import sys
import os
 
from subprocess import Popen, PIPE
 
process = Popen(['C:/Program Files/MATLAB/R2017b/bin/matlab.exe', '-nodesktop', '-nosplash', '-r', 
	              "run('C:/Distance2Go SW/v2.0.0/Firmware_Software/Communication Library/ComLib_Matlab_Interface/matlab/RadarSystemExamples/Radar-System/offline_testing/python_scripts/test_stream_data_python.m')" ], 
	              #stdout=PIPE, stderr=PIPE)
				  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()
while 1:
	print(stdout.decode('utf-8'))
	# nextline = process.stdout.readline()
	# print(nextline)
	# sys.stdout.write(nextline.decode('utf-8'))
	# sys.stdout.flush()

	with open('data_log.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			print(f'{row[0]}')
			line_count += 1
	print(f'Processed {line_count} lines.')