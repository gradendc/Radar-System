import subprocess
import sys
import os

p = subprocess.Popen(['C:/Program Files/MATLAB/R2017b/bin/matlab.exe', '-nodesktop', '-nosplash', '-r', "run('C:/Users/jmvsu/OneDrive/Documents/School_Fall_2018/elec_494/python_scripts/test_stream_data_python.m')" ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# matlab  = ['matlab']
# options = ['-nosplash', '-wait', '-r']
# command = ["run('C:/Users/jmvsu/OneDrive/Documents/School_Fall_2018/elec_494/python_scripts/test_stream_data_python.m')" >/dev/null'], stdout=subprocess.PIPE, stderr=subprocess.PIPE]
 
# p = Popen(matlab + options + command)

while 1:
	# try:
	# 	out, err = p.communicate()

	# except ValueError:
	# 	break
	# #print('message received')
	# print('message received' + out.decode('utf-8'))

	nextline = p.stdout.readline()
	print(nextline)
	sys.stdout.write(nextline.decode('utf-8'))
	sys.stdout.flush()