
import socket
import time
from threading import *

class SocketClient(Thread):
    def __init__(self, host, port, server_application):
        self.host = host
        self.port = int(port)
        self.connection = None
        self.t = None
        self.killed = False
        self.server_application = server_application

    def connect(self, server_id):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("Attempting to connect to %s:%s..."%(self.host, self.port))
            s.connect((self.host, self.port))
            s.send(f"connect {server_id}".encode())
            self.connection = s
            self.t = Thread(target=self.receive, args=(s,))
            self.t.start()
            return True
        except:
            pass
        return False


    def receive(self, client_socket, own_ip=None, own_port=None):
        while True:
            try:
                msg = client_socket.recv(1024).decode()
                if msg == "{quit}":
                    client_socket.close()
                    # if the server initiated the quit, then killed will still be false
                    if not self.killed:
                        self.killed = True
                        del self.chat_application.map_ip_to_server[(self.host, str(self.port))]
                        self.chat_application.connected_remote_hosts.remove((self.host, str(self.port)))
                        print("%s:%s terminated the connection"%(self.host, self.port))
                    return
                else:
                    self.server_application.rcv_packet_data(msg)
            except:
                return

    def send_message(self, message):
        if not self.connection:
            self.connect()
        if not self.connection:
            print("Was not able to connect to {self.host} {self.port}")
            return False
        try:
            self.connection.sendall(message.encode())
        except:
            return False
        return True

    def close(self):
        if self.t:
            try:
                self.killed = True
                self.send_message("{quit}")
                self.t.join()
            except:
                print("Error occured attempting to kill the thread.")
                return False
        if self.connection:
            try:
                self.connection.close()
            except:
                print("Error occured attempt to close the connection to remote host...")
                return False
        return True
