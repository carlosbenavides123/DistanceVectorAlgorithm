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

Carlos Benavides - created the interactive terminal (all commands), the reading of user input for when the server sets up (interval and filename), the TCP socket server and client, sending update to neighbors, neighbors handling updates, removing dead neighbors.
