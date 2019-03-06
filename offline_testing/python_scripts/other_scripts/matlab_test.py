import time
import matlab.engine
eng = matlab.engine.start_matlab()

#tf = eng.isprime(37)
#print(tf)

# for i in range(1,10):
# 	print('waiting...')
# 	time.sleep(2)
# tf = eng.isprime(37)
# print(tf)

#https://www.mathworks.com/help/matlab/matlab_external/redirect-standard-output-and-error-to-python.html
#https://www.mathworks.com/help/matlab/matlab_external/call-matlab-functions-asynchronously-from-python.html
#https://www.mathworks.com/matlabcentral/answers/324956-python-api-how-to-get-the-output

import io
out = io.StringIO()
err = io.StringIO()
future = eng.test_stream_data_python(nargout=0,stdout=out,stderr=err, async=True)
#future.result()
while not future.done():
	contents = out.getvalue()
	print("loop1")
	print("python print: ", contents)
print("script done running")

#ret = future.result()
#eng.test_stream_data_function(nargout=0)
#ret = eng.getData(); 
#print("python printing", ret)
