import io
from threading import Condition
import subprocess
import numpy as np
import cv2 as cv
from camera import Camera
from pyzbar.pyzbar import decode, ZBarSymbol
import json

hostnameFile = '/etc/hostname'
hostsFile = '/etc/hosts'
wpaFile = '/etc/wpa_supplicant/wpa_supplicant.conf'

camera = Camera()
frame_size = (640, 480)
frame_rate = 10

class StreamingOutput(object):
    # Streaming output object
    def __init__(self):
        self.buffer = io.BytesIO()
        self.qrValid = Condition()
        self.qrData = {}

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame
            self.buffer.truncate()
            # Reading QR
            frame = self.buffer.getvalue()
            self.read_qr(frame)
            print ('ok')
            # Reset buffer pointer
            self.buffer.seek(0)
        return self.buffer.write(buf)

    def read_qr(self, frame):
        npFrame = np.asarray(bytearray(frame))
        if npFrame.any():
            try:
                img = cv.imdecode(npFrame, 1)
                qr = decode(img, symbols = [ZBarSymbol.QRCODE])
                if len (qr) > 0:
                    data = (qr[0].data).decode()
                    data = json.loads(data)
                    self.qrData = data
                    print(self.qrData)
                    # Stopping camera
                    with self.qrValid:
                        self.qrValid.notify_all()                     
            except Exception as e:
                print (f'Qr detection error {e}')

def qr_process(qr_data):
    change_hostname(host_name = qr_data['host'], hostname_loc = hostnameFile, hosts_loc = hostsFile)
    set_network(wpa_loc=wpaFile, ssid=qr_data['ssid'], psk=qr_data['psk'])
    print ('Rebooting')
    subprocess.run(['sudo', 'reboot', 'now'])

def set_network(wpa_loc, ssid, psk):
    print ('Setting network')
    config_lines = [
        'network={\n'
        f'\tssid="{ssid}"\n'
        f'\tpsk="{psk}"\n'
        '}\n\n'
    ]
    # Read wpa file original content
     open (wpa_loc, 'r') as file:
        data = file.readlines()with
    # Modify data adnd write to temp file
    for line in config_lines:
        data.insert(4, line)
    with open ('wpa_temp', 'w') as file:
        file.writelines(data)
    # Replace hostname file with temp
    subprocess.run(['sudo', 'mv', 'wpa_temp', wpa_loc])
    
def change_hostname(host_name, hostname_loc, hosts_loc):
    print ('Setting host name')
    # Read hostname original content
    with open (hostname_loc, 'r') as file:
        data = file.readlines()
    # modify data and write to temp file
    data[0] = host_name
    with open ('temp', 'w') as file:
        file.writelines(data)
    # Replace hostname file with temp
    subprocess.run(['sudo', 'mv', 'temp', hostname_loc])
    # Read hosts original content
    with open (hosts_loc) as file:
        data = file.readlines()
    # modify data and write to temp file
    data[5] = '127.0.1.1    '+host_name
    with open ('temp', 'w') as file:
        file.writelines(data)
    # Replace hosts file with temp
    subprocess.run(['sudo', 'mv', 'temp', hosts_loc])

# Initialize streaming output object
output = StreamingOutput()

with output.qrValid:
    camera.start_camera(output, frame_size = frame_size, frame_rate = frame_rate)
    output.qrValid.wait(timeout=60) # timeout
    camera.stop_camera()
    qr_process(output.qrData)