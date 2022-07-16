from camera import Camera
from streamingoutput_basic import StreamingOutput
from threading import Thread
import websocket
import time

# Server host
serverHost = "192.168.25.102:8000"
# Camera object
camera = Camera()
# Frame size
frame_size = (640, 480)
# Frame rate
frame_rate = 20
# Streaming output object
output = StreamingOutput()

def on_message(wsapp, message):
    print (message)

try:
    # Start camera
    camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
    
    wsapp = websocket.WebSocketApp(f"ws://{serverHost}/ws/device1/", on_message=on_message)
    
    try:
        # Run the websocket in different thread
        wst = Thread(target = wsapp.run_forever)
        wst.start()
    except Exception as e:
        print (f'{e}: Failed starting websocket connection. closing connection')
        wsapp.close()
        wst = None

    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
            wsapp.send(frame) #, opcode=2)

except Exception as e:
    print (f'{e}: Camera Starting Error')
