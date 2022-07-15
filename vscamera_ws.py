from camera import Camera
from streamingoutput_basic import StreamingOutput
import asyncio
import websockets
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

# async def connect():
#     async with websockets.connect(f"ws://{serverHost}/ws/device1/") as websocket:
#         while True:
#             with output.condition:
#                 output.condition.wait()
#                 frame = output.frame
#                 await websocket.send(frame)


try:
    # Start camera
    camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
    
    #wsapp = websocket.WebSocketApp(f"ws://{serverHost}/ws/device1/")
    ws = websocket.WebSocket()
    ws.connect(f"ws://{serverHost}/ws/device1/")

    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
            ws.send(frame, opcode=2)
    # # Start thread for stream watcher
    # if not (t_watcher):
    #     t_watcher = Thread(target = watcher)
    #     t_watcher.start()

except Exception as e:
    print (f'{e}: Camera Starting Error')
