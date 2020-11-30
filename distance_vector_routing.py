import cmd, sys
import argparse
import os.path
import os
import sys
import threading
import socket
import collections
import datetime
import sys
import copy

# UDFs
from update_routing_table import update_routing_table
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
		self.parents = [None] * 4
		self.parents[self.server_id-1] = self.server_id

		self.topology = topology
		self.interval = int(interval)

		self.all_server_details = []
		self.not_listening_servers = set()

		self.connected_servers = {}

		self.amount_of_servers = 0
		self.amount_of_neighbors = len(self.all_server_details)

		self.read_topology_conf()

		self.fallback_graph = copy.deepcopy(self.graph)
		self.fallback_parents = self.parents[:]

		self.socket_server = SocketServer(self.server_ip, self.server_port, self)
		self.connect_to_servers()

		self.check_for_dead_server_packet_counter = 0
		self.is_blocked = False
		self.continue_broadcasting = True
		self.cron_broadcast_routing_update()

		self.packet_queue = collections.deque()
		self.cron_process_packet_queue()

		self.packet_count = 0
		self.packet_invocation_time = datetime.datetime.now()

		self.server_id_packet_counter = {server_id: 0 for server_id in range(1, 5) if server_id != self.server_id}

	def do_update(self, line):
		try:
			try:
				server_1, server_2, cost = line.split(" ")
			except:
				self.print_command_result(False, "Bad input, please input 'update <current_server_id> <neighbor_server_id> <cost>!")
			server_1 = int(server_1)
			server_2 = int(server_2)
			if server_1 != self.server_id:
				self.print_command_result(False, f"Cannot update {server_1} as server node {self.server_id}, this operation is not allowed.")
				return
			if server_2 not in self.graph[server_1]:
				self.print_command_result(False, f"Cannot update {server_1} as server node {server_2} are not neighbors.")
				return

			try:
				cost = float(cost)
			except:
				self.print_command_result(False, "Bad input for cost, please input a valid number for updating link cost!")

			if type(cost) == float and cost > 0:
				if cost != float("inf"):
					cost = int(cost)
					self.update_link_cost(server_1, server_2, cost)
				else:
					# update the links to be inf
					cost = -1
					self.update_link_cost(server_1, server_2, cost)
				self.send_update_message(server_1, server_2, cost)
				self.print_command_result(True)
			else:
				self.print_command_result(False, "Bad input for cost, please input a valid number for updating link cost!")
				return
		except Exception as ex:
			self.print_command_result(False, ex)

	def update_link_cost(self, server_1, server_2, cost):
		if server_2 in self.graph[server_1]:
			if cost != -1:
				try:
					self.graph[server_1][server_2] = cost
					self.graph[server_2][server_1] = cost
					self.fallback_graph[server_1][server_2] = cost
					self.fallback_graph[server_2][server_1] = cost
				except:
					return False
			elif cost == -1:
				try:
					del self.graph[server_1][server_2]
					del self.graph[server_2][server_1]
					del self.fallback_graph[server_1][server_2]
					del self.fallback_graph[server_2][server_1]
				except:
					return False
			return True
		return False

	def send_update_message(self, server_1, server_2, cost):
		connected_server = self.connected_servers[server_2]
		update_message = "{update}" + " " + str(server_1) + " " + str(server_2) + " " + str(cost)
		if isinstance(connected_server, SocketClient):
			connected_server.send_message(update_message, self.server_id)
		else:
			self.socket_server.send_message(connected_server, update_message, self.server_id)

	def rcv_packet_data(self, msg):
		try:
			# dictionary message
			data, server_id  = msg.split("#")
			server_id = int(server_id)
			print(f"RECEIVED A MESSAGE FROM SERVER {server_id} {data}")
			data = eval(data)
			self.packet_queue.append(data)
		except:
			return

	def connect_to_servers(self):
		for server_id, server_ip, server_port in self.all_server_details:
			if server_ip == self.server_ip and server_port == self.server_port:
				pass
			else:
				if server_id in self.not_listening_servers:
					continue
				socket_client = SocketClient(server_ip, server_port, self)
				if socket_client.connect(self.server_id):
					print("Successfully connected to %s:%s"%(server_ip, server_port))
					self.connected_servers[server_id] = socket_client
				else:
					print("Connection to %s:%s failed!"%(server_ip, server_port))

	def do_step(self, line):
		try:
			print("Sending update to neighbors.")
			self.cron_broadcast_routing_update()
			self.print_command_result(True)
		except Exception as ex:
			self.print_command_result(False, ex)

	def do_packets(self, line):
		try:
			print(f"{self.packet_count} packets have been received since {self.packet_invocation_time}.")
			self.packet_count = 0
			self.packet_invocation_time = datetime.datetime.now()
			self.print_command_result(True)
		except Exception as ex:
			self.print_command_result(False, ex)

	def do_display(self, line):
		try:
			print('Destination ID    Next Hop ID       Cost')
			f = '{:<15}   {:<15}      {:<5}' #format
			src_vector = self.graph[self.server_id]

			for i in range(1, len(self.all_server_details)+1):
				if i == self.server_id:
					print(f.format(*[i, i, 0]))
				elif i not in src_vector:
					print(f.format(*[i, "N/A", float("inf")]))
				else:
					print(f.format(*[i, self.parents[i-1], src_vector[i]]))
			self.print_command_result(True)
		except Exception as ex:
			self.print_command_result(False, ex)

	def do_disable(self, line):
		message = str(self.server_id) + " " + str(line) + " " + "inf"
		self.do_update(message)

	def do_crash(self, line):
		print("Crashing...")
		self.do_exit("")
		return -1

	def do_exit(self, line):
		print("Exiting application...")
		self.continue_broadcasting = False
		for connected_server_id, connected_server in self.connected_servers.items():
			self.do_disable(connected_server_id)
		self.socket_server.stop()
		return -1

	def print_command_result(self, success, error_msg=""):
		if self.is_blocked:
			return
		if success and self._hist:
			print(f"{self._hist[-1]} SUCCESS")
		else:
			if self._hist:
				print(f"{self._hist[-1]} ERROR: {error_msg}")

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
							self.not_listening_servers.add(neighbor_server_id)
							continue
						graph[server_id].update({neighbor_server_id: cost})
						graph[neighbor_server_id].update({server_id: cost})
						self.parents[neighbor_server_id-1] = neighbor_server_id
				count += 1

		# update the state variables
		self.all_server_details = all_server_details
		self.graph = graph
		print("initial routing table...", self.graph)
		
	def cron_broadcast_routing_update(self):
		if self.continue_broadcasting:
			if not self.is_blocked:
				for key, connected_server in self.connected_servers.items():
					src_vector = self.graph[self.server_id]
					message = str({self.server_id: src_vector})

					if isinstance(connected_server, SocketClient):
						connected_server.send_message(message, self.server_id)
					else:
						self.socket_server.send_message(connected_server, message, self.server_id)
			threading.Timer(self.interval, self.cron_broadcast_routing_update).start()

	def cron_process_packet_queue(self):
		self.check_for_dead_server_packet_counter += 1
		if self.continue_broadcasting:
			
			if self.packet_queue:
				self.packet_count += 1
				nei_vector_data = self.packet_queue.popleft()
				new_graph, new_parents, reset = update_routing_table(self.graph, self.server_id, nei_vector_data, self.parents)
				self.graph = new_graph
				self.parents = new_parents

				for nei_server_id in nei_vector_data:
					self.server_id_packet_counter[nei_server_id] += 1
				if reset:
					print("resetting..")
					self.packet_queue.clear()

			if self.check_for_dead_server_packet_counter >= 100:
				self.check_for_dead_servers()
			threading.Timer(0.1, self.cron_process_packet_queue).start()

	def check_for_dead_servers(self):
		self.is_blocked = True
		if self.continue_broadcasting:
			new_graph = self.graph.copy()
			nei_packets_count = self.server_id_packet_counter.copy()
			self.server_id_packet_counter = {server_id: 0 for server_id in range(1, 5) if server_id != self.server_id}

			will_fallback = False
			for server_id, count in nei_packets_count.items():
				if count < 3:
					print("Lost server id ", server_id)
					for key in self.graph:
						if server_id in self.fallback_graph[key]:
							del self.fallback_graph[key][server_id]
							will_fallback = True
					if server_id in self.fallback_graph:
						del self.fallback_graph[server_id]
					if server_id in self.connected_servers:
						self.do_disable(str(server_id))
					self.packet_queue.clear()
			self.graph = copy.deepcopy(self.fallback_graph)

			for nei_server_id in self.connected_servers:
				if nei_server_id in self.graph[self.server_id]:
					message = str(self.server_id) + " " + str(nei_server_id) + " " + str(self.graph[self.server_id][nei_server_id])
					self.do_update(message)
			self.parents = self.fallback_parents

		self.check_for_dead_server_packet_counter = 0
		self.is_blocked = False
		print("Checking for dead servers completed...")

	def preloop(self):
		cmd.Cmd.preloop(self)
		self._hist = []

	def precmd(self, line):
		if line != '':
			self._hist.append(line.strip())
		return line

	def emptyline(self):
			pass

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
