# matlab_data_logger.py
from multiprocessing.connection import Client
import zmq, json

SERVER_ADDRESS = '18.237.234.155'
SERVER_PORT = '2344'

context = zmq.Context()
radar_socket = context.socket(zmq.PUB)
radar_socket.connect('tcp://' + SERVER_ADDRESS + ':' + SERVER_PORT)


"""Python module demonstrates passing MATLAB types to Python functions"""
def sendData(self, timeString, respRate, rateMag, phasePointVector):
    """Return data if transfered data, return 0 if failed"""
    frameDict = {
        'phasePointVector': phasePointVector.tolist(),
        'timeString': timeString,
        'respRate': respRate,
        'rateMag': rateMag
    }
    frameDictJSON = json.dumps(frameDict)

    radar_socket.send_string(frameDictJSON)
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
