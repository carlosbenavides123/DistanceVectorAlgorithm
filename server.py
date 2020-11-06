import cmd, sys
import argparse
import os.path
import os
import sys
import threading

from os import path

class Server(cmd.Cmd):
	def __init__(self, topology, interval):
		cmd.Cmd.__init__(self)
		self.prompt = ">> "
		self.intro = "Welcome to Chat Application!"

		self.topology = topology
		self.interval = interval

		self.neighbor_details = []
		self.amount_of_servers = 0
		self.amount_of_neighbors = len(self.neighbor_details)

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

	def read_topology_conf(self):
		count = 0
		with open(self.topology) as fp:
			for line in fp:
				line = line.replace('\n','')
				if count == 0:
					self.amount_of_servers = int(line)
				elif count == 1:
					self.amount_of_neighbors = int(line)
				elif line != '':
					server_id, server_ip, port = line.split(" ")
					self.neighbor_details.append((server_id, server_ip, port))
				count += 1

	def update_topology_file_conf(self):
		f = open(self.topology, "w+")
		f.writelines(f"{self.amount_of_servers}\n")
		f.writelines(f"{self.amount_of_neighbors}\n")
		for nei in self.neighbor_details:
			f.writelines(" ".join(map(str, nei)) + "\n")
		f.close()

	def cron_update_topology_state(self):
		threading.Timer(self.interval, self.cron_update_topology).start()
		print("im called!")

	# def parse_topology_conf(self):
	# 	with open(self.topology) as fp:
	# 		line = fp.readline()
	# 		while line:
	# 			print(line.strip())

	# def write_to_topology_conf(self):
	# 	with open(self.topology) as fp:

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
