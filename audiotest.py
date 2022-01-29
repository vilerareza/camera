import sounddevice as sd

duration = 10 # seconds
fs = 44100

r = sd.rec(int(duration*fs), samplerate=fs, channels=2)
sd.wait()
print (len(r))
sd.play(r, fs)
sd.wait()
#def callback(indata, outdata, frames, time, status):
#    if status:
#        print(status)
#        outdata[:] = indata

#myStream = sd.RawStream(channels=2, callback=callback)
#myStream.start()
#sd.sleep(int(duration * 1000))
#with sd.RawStream(channels=2, callback=callback):
#    sd.sleep(int(duration * 1000))
