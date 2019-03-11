# matlab_data_logger.py
from multiprocessing.connection import Client
import time

"""Python module demonstrates passing MATLAB types to Python functions"""
def sendData(timeString, respRate, phasePointVector):
    """Return data if transfered data, return 0 if failed"""
    address = ('localhost', 6000)
    conn = Client(address, authkey=b'secret password')
    #conn.send('close')
    conn.send(timeString)
    conn.send(respRate)
    conn.send(phasePointVector)
    conn.close()

    return respRate

#enter this code into matlab command prompt to enter current directory 
#into python search path:
#if count(py.sys.path,'') == 0
#    insert(py.sys.path,int32(0),'');
#end

#enter this code into matlab command prompt to reload the python script 
#after edits (replace dataLogger with script name):
#clear classes
#mod = py.importlib.import_module('dataLogger');   
#py.importlib.reload(mod);