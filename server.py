# Import the argparse library
import argparse
import os.path
import os
import sys

from os import path

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

	print("args outside of main:")
	print(topology)
	print(interval)
