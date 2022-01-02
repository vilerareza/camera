import threading
import socket
import selectors


def __accept_wrapper(sock):
    # accept new connections
    conn, addr = sock.accept()
    print ('accepted connection from ', addr)
    conn.setblocking(False)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn,events, data = addr)


def __service_connection (key, mask):
    print('service connection called')
# Receive data
    sock = key.fileobj
    data = key.data
    #try:
    camfile1 = sock.makefile('rb')
    camfile1.read()
'''
       if mask & selectors.EVENT_READ:
            #receiving data
            camData = camfile1.read() 
            self.__write(camData)
            #check the camera connection
            sock.send(b'1')
            print('b1 sent')
        except:
            print ('closing connection to ', data)
            self.sel.unregister(sock)
            sock.close()
            with self.statusChange:
                self.status = 'No Camera Connection'
                self.statusChange.notify_all()
            self.frameInitialized = False
'''

def listen_from_socket():
    '''
    Listen for new connection
    '''
    global comSocket
    global host
    global port
    global sel
    comSocket.bind((host,port))
    comSocket.listen()
    print('listening on, ', (host,port))
    comSocket.setblocking(False)
    sel.register(comSocket, selectors.EVENT_READ, data = None)
    while True:
        events = sel.select(timeout = None) #this blocks
        for key, mask in events:
            if key.data is None:
                __accept_wrapper(key.fileobj)
            else:
                __service_connection(key, mask)

def start_socket_thread():
    '''
    Start the socket listening thread
    '''
    global t_socket_listen
    if not (t_socket_listen):
        t_socket_listen = threading.Thread(target = listen_from_socket)
        t_socket_listen.start()
        print('Socket thread running: '+str(t_socket_listen.is_alive()))


t_socket_listen = None
comSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 65001
sel = selectors.DefaultSelector()


#start_socket_thread()
listen_from_socket()
