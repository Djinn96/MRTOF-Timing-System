import socket
from .threadinglib import ThreadWithResult

FORMAT = 'utf-8'
HEADER = 256

class timingTCPSocket:
    def __init__(self,ip:str,port:int):
        self.addr = (ip,port)

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.addr)
            if __debug__: print("[CONNECT] Connected to {}".format(self.addr))
        except:
            print("[CONNECT FAIL] IP not found! addr:",self.addr)

    def close(self):
        self.socket.close()
        if __debug__: print("[CLOSE] Connection to {} closed.".format(self.addr))

    def send(self,message:str):
        msg = message.encode(FORMAT)
        if __debug__: print("[SEND] Sending message to {}: {}".format(self.addr,msg))
        self.socket.send(msg)

    def listen(self):
        if __debug__: print("[LISTEN] waiting for message from {}".format(self.addr))
        msg = self.socket.recv(HEADER)
        if __debug__: print("[{}] {}".format(self.addr,msg))
        result = msg
        return result
    
    def sendWaitResponse(self,message:str):
        # Start a listening thread before sending command to ensure response is captured
        listenThread = ThreadWithResult(target=self.listen)
        listenThread.start()
        # Send message
        self.send(message)

        response:str = listenThread.join()
        
        return response.decode().strip('\r')