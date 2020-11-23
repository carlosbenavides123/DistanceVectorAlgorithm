import socket, time
import bisect
from threading import *
from multiprocessing import *

class SocketServer(Thread):
    def __init__(self, host, port, server_application):
        Thread.__init__(self)
        self.host = host
        self.port = int(port)
        self.server_application = server_application
        self.killed = False
        self.start()
        self.clients = {}
        self.server_id = ""

    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen()
        while True:
            try:
                conn, addr = self.s.accept()
                ip, port = addr
                port = str(port)
                print("%s made a connection with you."%ip)
                Thread(target=self.handle_client, args=(conn, addr)).start()
            except Exception:
                print("Shutting down server...")
                break

    def handle_client(self, client, addr):
        """Handles a single client connection."""
        ip, port = addr
        port = str(port)
        while True:
            try:
                msg = client.recv(1024).decode()
            except:
                return
            if msg.startswith("connect"):
                _, server_id = msg.split(" ")
                # initial message for when a client attempts to connect to server
                self.server_application.connected_servers[server_id] = client
                continue
            elif msg.startswith("{quit}"):
                _, server_id = msg.split("#")
                self.close_connection(client)
                print(f"Server id {server_id} {ip}:{port} terminated the connection")
                return
            else:
                self.server_application.rcv_packet_data(msg)

    def send_message(self, client, message, server_id):
        try:
            self.server_id = server_id
            message = str(message) + "#" + str(server_id)
            client.send(message.encode())
        except:
            return False
        return True

    # def broadcast(self, msg):
    #     """Broadcasts a message to all the clients."""
    #     # print(msg.decode())
    #     for sock in self.clients:
    #         sock.send(msg)

    def close_connection(self, client):
        try:
            self.send_message(client, "{quit}", self.server_id)
            client.close()
        except:
            return False
        return True

    def stop(self):
        self.s.close()
