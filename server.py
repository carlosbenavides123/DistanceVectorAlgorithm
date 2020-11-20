import cmd, sys
import argparse
import os.path
import os
import sys
import threading
import socket
import collections

# UDFs
from bellman_ford import bellman_ford, update_routing_table
from socket_server import SocketServer
from socket_client import SocketClient

from os import path

class Server(cmd.Cmd):
	def __init__(self, topology, interval):
		cmd.Cmd.__init__(self)
		self.prompt = ">> "

		self.server_ip = socket.gethostbyname(socket.gethostname())
		if self.server_ip == "127.0.0.1":
			try:
				self.server_ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
			except Exception:
				print("Was not able to find a valid client ip...")

		self.server_id = 0
		self.server_port = 0

		self.graph = collections.defaultdict(dict)

		self.topology = topology
		self.interval = int(interval)

		self.all_server_details = []
		self.connected_servers = {}

		self.amount_of_servers = 0
		self.amount_of_neighbors = len(self.all_server_details)

		self.read_topology_conf()
		# self.update_topology_file_conf()

		self.socket_server = SocketServer(self.server_ip, self.server_port, self)
		self.connect_to_servers()

		self.continue_broadcasting = True
		self.cron_broadcast_routing_update()

		self.packet_queue = collections.deque()
		self.cron_process_packet_queue()

	def do_update(self, line):
		print("do update")

	def rcv_packet_data(self, msg):
		try:
			# dictionary message
			data = eval(msg)
			self.packet_queue.append(data)
		except:
			return

	def connect_to_servers(self):
		for server_id, server_ip, server_port in self.all_server_details:
			if server_ip == self.server_ip and server_port == self.server_port:
				pass
			else:
				socket_client = SocketClient(server_ip, server_port, self)
				if socket_client.connect(self.server_id):
					print("Successfully connected to %s:%s"%(server_ip, server_port))
					self.connected_servers[server_id] = socket_client
				else:
					print("Connection to %s:%s failed!"%(server_ip, server_port))

	def do_sent(self, line):
		print(self.all_server_details)

	def do_step(self, line):
		print("do step")

	def do_packets(self, line):
		print("do packets")

	def do_display(self, line):
		print("do display")
		print(self.graph)

	def do_disable(self, line):
		print("do disable")

	def do_crash(self, line):
		print("do crash")

	def do_exit(self, line):
		print("stopping tcp server connection")
		self.socket_server.stop()
		self.continue_broadcasting = False
		return -1

	def read_topology_conf(self):
		count = 0
		all_server_details = []
		graph = collections.defaultdict(dict)

		with open(self.topology) as fp:
			for line in fp:
				line = line.replace('\n','')
				line = line.strip()
				if count == 0:
					self.server_id = int(line)
				elif count == 1:
					self.amount_of_servers = int(line)
				elif count == 2:
					self.amount_of_neighbors = int(line)
				elif line != '' and len(line.split(" ")) == 3:
					# differentiate the line of server id and ip, port pair
					# and the server id, neighbor id, and cost line
					server_id, val_pos_2, val_pos_3 = line.split(" ")
					server_id = int(server_id)
					# server id, ip and port pair
					if len(val_pos_2) > 2:
						server_ip = val_pos_2
						server_port = val_pos_3
						# get the server's data
						# otherwise append/update the neighbor details
						# if server_ip == self.server_ip:
						if self.server_id == server_id:
							self.server_id = server_id
							self.server_port = server_port
						all_server_details.append((server_id, server_ip, server_port))
					else:
						# server id, neighbor id, and cost
						neighbor_server_id = int(val_pos_2)
						cost = int(val_pos_3)
						if cost == -1:
							cost = float("inf")
						graph[server_id].update({neighbor_server_id: cost})
						graph[neighbor_server_id].update({server_id: cost})
				count += 1

		# update the state variables
		self.all_server_details = all_server_details
		self.graph = graph
		print("initial routing table...", self.graph)

	def update_topology_file_conf(self):
		f = open(self.topology, "w+")
		f.writelines(f"{self.amount_of_servers}\n")
		f.writelines(f"{self.amount_of_neighbors}\n")
		for nei in self.all_server_details:
			f.writelines(" ".join(map(str, nei)) + "\n")
		for node in self.graph:
			for nei, cost in self.graph[node]:
				f.writelines(str(node) + " " + str(nei) + " " + str(cost) + "\n")
		f.close()
		
	def cron_broadcast_routing_update(self):
		if self.continue_broadcasting:
			threading.Timer(self.interval, self.cron_broadcast_routing_update).start()
			for key, connected_server in self.connected_servers.items():
				src_vector = self.graph[self.server_id]
				message = str({self.server_id: src_vector})

				if isinstance(connected_server, SocketClient):
					connected_server.send_message(message)
				else:
					self.socket_server.send_message(connected_server, message)

	def cron_process_packet_queue(self):
		print("cron")
		if self.continue_broadcasting:
			threading.Timer(0.1, self.cron_process_packet_queue).start()
			if self.packet_queue:
				print("yes")
				nei_vector_data = self.packet_queue.popleft()
				print("processing...", nei_vector_data)
				self.graph = update_routing_table(self.graph, self.server_id, nei_vector_data)

def check_positive_interval(interval):
	try: 
		num = int(interval)
		if num <= 0:
			return False
		return True
	except ValueError:
		return False

def check_topology_file_exists(topology):
	if path.exists(topology):
		return True
	return False

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='The server for Distance Vector Comp 429 Project.')
	parser.add_argument('-t', '--topology', required=True, help='(Required) The topology configuration file.')
	parser.add_argument('-i', '--interval', required=True, help='(Required) The interval to update the server in seconds.')

	args = parser.parse_args()
	topology = args.topology
	interval = args.interval

	if not check_positive_interval(interval):
		raise argparse.ArgumentTypeError(f"{interval} is an invalid positive int value, please enter a value greater than 0.")
	if not check_topology_file_exists(topology):
		raise argparse.ArgumentTypeError(f"{topology} does not exist in path, please enter the correct file name in path.")

	print("creating server...")
	Server(topology, interval).cmdloop()
