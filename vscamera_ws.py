from camera import Camera
from streamingoutput_basic import StreamingOutput
import asyncio
import websockets

# Server host
serverHost = "192.168.4.102:8000"
# Camera object
camera = Camera()
# Frame size
frame_size = (640, 480)
# Frame rate
frame_rate = 10
# Streaming output object
output = StreamingOutput()

async def connect():
    async with websockets.connect(f"ws://{serverHost}/ws/device1/") as websocket:
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
                await websocket.send(frame)

try:
    # Start camera
    camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
    asyncio.run (connect())
    # # Start thread for stream watcher
    # if not (t_watcher):
    #     t_watcher = Thread(target = watcher)
    #     t_watcher.start()

except Exception as e:
    print (f'{e}: Camera Starting Error')
