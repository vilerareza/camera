import socket
import time
import picamera

address = ('192.168.2.102', 65003)
#address = ('20.85.215.205', 65003)
#address = ('156.67.217.141', 65003)
#address = ('52.224.63.202', 65003)
#address = ('viewsense-rv.eastus.cloudapp.azure.com', 65003)
ssocket = None
connection = None
camera = None

camera = picamera.PiCamera()
camera.resolution = (640,480)
camera.framerate = 15

print('connecting')
ssocket = socket.socket()
ssocket.connect(address)

'''
while (True):

    try:
        ssocket = socket.socket()
        #setting timeout
        ssocket.settimeout(3)
        print('connecting')
        ssocket.connect(address)
        #file like object
        connection = ssocket.makefile('wb')
        #start the cam
        camera = picamera.PiCamera()
        camera.resolution = (640,480)
        camera.framerate = 5
        #camera.start_preview(layer = 1, alpha = 200, fullscreen = False, window = (320,240, 320, 240))
        time.sleep(2)
        camera.start_recording(connection, format = 'mjpeg')

        print('start recording')
        camera.wait_recording(300)
        print('end recording')


    except Exception as e:
        pass
        #print(e)
        #print('exception')

    finally:
        pass
        if (camera):
            try:
                print ('ending camera')
                camera.stop_recording()
                #camera.stop_preview()
            except Exception as e:
                print (e)
                print ('camera close error')
            finally:
                camera.close()
                camera = None

        if (connection):
            try:
                print ('ending connection')
                connection.close()
            except Exception as e:
                print (e)
                print ('connection close error')
            finally:
                ssocket.close()
                ssocket=None
        '''


