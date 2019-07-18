import subprocess
import os

p = subprocess.Popen(['C:\Program Files\MATLAB\R2017b\bin\matlab.exe', '-nodesktop', '-nosplash', '-r "run('C:\Distance2Go SW\v2.0.0\Firmware_Software\Communication Library\ComLib_Matlab_Interface\matlab\RadarSystemExamples\GettingStarted\extract_raw_data_python.m')" >/dev/null'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
while 1:
	try:
		out, err = p.communicate()

	except ValueError:
		break
	print('message received' + out)