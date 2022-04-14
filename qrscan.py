from camera import Camera

camera = Camera()
# Frame size
frame_size = (320, 240)
# Frame rate
frame_rate = 15

# Start camera
camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)