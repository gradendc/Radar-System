import subprocess
import sys
import os
 
from subprocess import Popen, PIPE
 
process = Popen(['C:/Program Files/MATLAB/R2017b/bin/matlab.exe', '-nodesktop', '-nosplash', '-r', 
	              "run('C:/Distance2Go SW/v2.0.0/Firmware_Software/Communication Library/ComLib_Matlab_Interface/matlab/RadarSystemExamples/Radar-System/offline_testing/python_scripts/test_stream_data_python.m')" ], 
	              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	              #stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()
while 1:
	print(stdout.decode('utf-8'))
	# nextline = process.stdout.readline()
	# print(nextline)
	# sys.stdout.write(nextline.decode('utf-8'))
	# sys.stdout.flush()