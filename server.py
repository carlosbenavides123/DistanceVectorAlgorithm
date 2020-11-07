import cmd, sys
import argparse
import os.path
import os
import sys
import threading
import socket
import collections

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

		self.graph = collections.defaultdict(list)

		self.topology = topology
		self.interval = interval

		self.all_server_details = []
		self.amount_of_servers = 0
		self.amount_of_neighbors = len(self.all_server_details)

		self.read_topology_conf()
		self.update_topology_file_conf()

	def do_update(self, line):
		print("do update")

	def do_step(self, line):
		print("do step")

	def do_packets(self, line):
		print("do packets")

	def do_display(self, line):
		print("do display")

	def do_disable(self, line):
		print("do disable")

	def do_crash(self, line):
		print("do crash")

	def do_exit(self, line):
		return -1

	def do_debug(self, line):
		print(f"server_id {self.server_id}, server_port {self.server_port}, amt_of_servers {self.amount_of_servers}, amt_of_nei {self.amount_of_neighbors}, nei details {self.all_server_details}, graph {self.graph}")

	def read_topology_conf(self):
		count = 0
		all_server_details = []
		graph = collections.defaultdict(list)

		with open(self.topology) as fp:
			for line in fp:
				line = line.replace('\n','')
				line = line.strip()
				if count == 0:
					self.amount_of_servers = int(line)
				elif count == 1:
					self.amount_of_neighbors = int(line)
				elif line != '' and len(line.split(" ")) == 3:
					# differentiate the line of server id and ip, port pair
					# and the server id, neighbor id, and cost line
					server_id, val_pos_2, val_pos_3 = line.split(" ")
					# server id, ip and port pair
					if len(val_pos_2) > 2:
						server_ip = val_pos_2
						server_port = val_pos_3
						# get the server's data
						# otherwise append/update the neighbor details
						if server_ip == self.server_ip:
							self.server_id = server_id
							self.server_port = server_port
						all_server_details.append((server_id, server_ip, server_port))
					else:
						# server id, neighbor id, and cost
						neighbor_server_id = val_pos_2
						cost = val_pos_3
						graph[server_id].append((neighbor_server_id, cost))
				count += 1

		# update the state variables
		self.all_server_details = all_server_details
		self.graph = graph

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

	def cron_update_topology_state(self):
		threading.Timer(self.interval, self.cron_update_topology).start()
		print("im called!")

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
