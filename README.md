# How program is built
In this project, the main focus is designing a network topology of 4 servers/laptops that implements a simplified version of the distance Vector Routing Protocol using TCP aswell. The main driver program of it is called the distance_vector_routing.py that utilizes the server and client socket files to serve as the hosts that will be connecting to the overall network topology. The update_routing_table.py is used to update each individual node's forwarding table regarding all the others nodes position from the specific node's perspective. How the main program works is that it takes in a local topology text file with a specific format that tells it how many neighbors it has and their costs to each of them. If the server is not a neighbor, then its initial cost would be infinity, or in our project we define it as -1. Each server instantiated can only read its own topology file for itself and must update the rest through the rest of the servers connecting to it. 
# How to run this application

Please have python installed (preferrably python 3)

cd to the program directory

to run server 1 for example...

python3 ./distance_vector_routing.py -t server_1.txt -i 2

-t <filename> specifies the filename for the initial file
-i <number> specifies the interval to send updates to neighbors

and to run server 2 (and so forth...)
python3 ./distance_vector_routing.py -t server_2.txt -i 2

python3 ./distance_vector_routing.py -t server_3.txt -i 2

python3 ./distance_vector_routing.py -t server_4.txt -i 2

# Contributions

Carlos Benavides - created the interactive terminal (all commands), the reading of user input for when the server sets up (interval and filename), the TCP socket server and client, sending update to neighbors, neighbors handling updates, removing dead neighbors, recorded and uploaded video

Alfredo Sanchez - Test and run all the programs with the topology files altered to my own ip to verify that it is working as intended. Attempted to implement a solution to fix the initial delay problem once a second server updates the first server, however this may be due to innate problem the distance protocol has of lagging to update other servers. Furthermore, contributed to the README file of the programs structure.
