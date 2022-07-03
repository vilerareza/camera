from camera import Camera
from streamingoutput_basic import StreamingOutput
import asyncio
import websockets

# Camera object
camera = Camera()
# Frame size
frame_size = (640, 480)
# Frame rate
frame_rate = 5
# Streaming output object
output = StreamingOutput()

async def connect():
    async with websockets.connect("ws://localhost:8000/ws/") as websocket:
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
                websocket.send_byte(frame)

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
