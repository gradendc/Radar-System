import time
import matlab.engine
eng = matlab.engine.start_matlab()

tf = eng.isprime(37)
print(tf)

# for i in range(1,10):
# 	print('waiting...')
# 	time.sleep(2)
# tf = eng.isprime(37)
# print(tf)

eng.extract_raw_data_python(nargout=0); 

#ret = future.result()
#eng.test_stream_data_function(nargout=0)
#ret = eng.getData(); 
#print("python printing", ret)
