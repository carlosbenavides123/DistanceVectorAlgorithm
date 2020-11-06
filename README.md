1) Each server is supplied a topology file - used to build initial routing table
2) This file is local and contains consts to each neighbor if available else infinity
3) Each server can read the topology file for itself

Structure of such topology file

<num-servers>
<num-neighbors> - 
<server-ID><server-IP><server-port>
<server-ID1><server-ID2><cost>

Explanation
<num-servers> - total number of servers
<server-ID><server-ID1><server-ID2> - uuid for a server, assigned by you
<cost> - cost of a given link pair

Line number             Line entry                                Comments
1                       4                                         number of servers
2                       3                                         number of edges or neighbors
3                       1 192.168.0.169 4091                      server-id 1 and corresponding IP, port pair


basically
the topo file will be null ? or hardcoded at the beginning... not sure
when a server doesnt send updates for 3 consect turns, remove it from the table and network (make the cost infinite, not actually remove)

run like...
server -t <topology-file-name> -i <routing-update-interval>
topology-file-name: The topology file contains the initial topology configuration for the
server, e.g., timberlake_init.txt. Please adhere to the format described in 3.1 for your topology
files.
routing-update-interval: It specifies the time interval between routing updates in seconds.
port and server-id: They are written in the topology file. The server should find its port and
server-id in the topology file without changing the entry format or adding any new entries.

todo:

<!-- make the 
server -t <topology-file-name> -i <routing-update-interval>
functionality work -->

be able to parse and use the topology file
use the timer to update the server state every <interval> time
