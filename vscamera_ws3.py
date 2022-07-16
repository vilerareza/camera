from camera import Camera
from streamingoutput_basic import StreamingOutput
from threading import Thread
import websocket

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
    
    # Websocket App
    wsapp = websocket.WebSocketApp(f"ws://{serverHost}/ws/control/device1/", on_message=on_message)
    try:
        # Run the websocket in different thread
        wst = Thread(target = wsapp.run_forever)
        wst.start()
    except Exception as e:
        print (f'{e}: Failed starting websocketapp connection. closing connection')
        wsapp.close()
        wst = None
    
    # Websocket
    ws = websocket.WebSocket()
    ws.connect(f"ws://{serverHost}/ws/frame/device1/")

    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
            ws.send(frame, opcode=2)

except Exception as e:
    print (f'{e}: Camera Starting Error')
