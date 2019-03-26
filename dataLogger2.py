import zmq

SERVER_ADDRESS = '127.0.0.1'
PORT = '6000'

context = zmq.Context()
footage_socket = context.socket(zmq.PUB)
footage_socket.connect('tcp://' + SERVER_ADDRESS + ':' + SERVER_PORT)


"""Python module demonstrates passing MATLAB types to Python functions"""
def sendData(timeString, respRate, rateMag, phasePointVector):
    """Return data if transfered data, return 0 if failed"""
    frameDict = {
        'phasePointVector': phasePointVector,
        'timeString': timeString,
        'respRate': respRate,
        'rateMag': rateMag
    }
    frameDictJSON = json.dumps(frameDict)

    footage_socket.send_string(frameDictJSON)


return respRate