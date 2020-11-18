import collections

# -1 error
# 0 success
def update_routing_table(graph, src_server_id, src_nei_vector):
    print(graph)
    print("----")
    src_nei_key = None
    for key in src_nei_vector:
        src_nei_key = key
    if src_nei_key == None:
        # raise error
        return -1

    if src_nei_key in graph[src_server_id] and src_server_id in src_nei_vector[src_nei_key]:
        graph[src_server_id].update({src_nei_key: 
                min(graph[src_server_id][src_nei_key], src_nei_vector[src_nei_key][src_server_id])
            })

    nei_vector = src_nei_vector[src_nei_key]
    src_vector = graph[src_server_id]
    new_min_src_vector = {}

    src_to_nei_cost = float("inf")
    for key, cost in src_vector.items():
        if src_nei_key == key:
            src_to_nei_cost = cost
            new_min_src_vector[src_nei_key] = graph[src_server_id][src_nei_key]
            break
    if src_to_nei_cost == float("inf"):
        # raise error
        print("error src_to_nei_cost float inf")
        return -1
    print("src vect ", src_vector)
    print("nei vect ", nei_vector)
    print("new_min_src_vector ", new_min_src_vector)

    src_vector_keys = set([key for key in src_vector])

    for nei_nei_node, nei_nei_cost in nei_vector.items():
        if nei_nei_node == src_server_id:
            continue

        if nei_nei_node not in src_vector_keys:
            new_min_src_vector[nei_nei_node] = nei_nei_cost + src_to_nei_cost
        else:
            for src_vector_nei, src_vector_nei_cost in src_vector.items():
                if src_vector_nei == nei_nei_node:
                    if src_vector_nei_cost > nei_nei_cost + src_to_nei_cost:
                        new_min_src_vector[src_vector_nei] = nei_nei_cost + src_to_nei_cost
                    else:
                        new_min_src_vector[src_vector_nei] = src_vector_nei_cost
                    break

    graph[src_server_id] = new_min_src_vector
    graph[src_nei_key] = nei_vector
    print(graph)
    return 0

# not sure if needed, this was used for a bellman ford algorithm assuming we know all values at compile/interpret time
# this does not seem to be the case as we rely on other nodes in run time to give us all the information
# we need for this project

def bellman_ford(graph, src_server_id):
    for nei in graph:
        if nei == src_server_id:
            continue
        else:
            update_nei_vector = {}
            for other_nei_node in graph:
                if other_nei_node == src_server_id or other_nei_node == nei:
                    continue
                if nei in graph[other_nei_node] and other_nei_node not in graph[nei]:
                    update_nei_vector.update({other_nei_node: graph[other_nei_node][nei]})
            for nei_nei_node, nei_node_cost in graph[nei].items():
                if nei_nei_node == src_server_id and nei in graph[src_server_id]:
                    update_nei_vector.update({nei_nei_node:
                        min(graph[src_server_id][nei], nei_node_cost)
                    })
                else:
                    update_nei_vector.update({nei_nei_node: nei_node_cost})
            graph[nei] = update_nei_vector
    print(graph)
    return graph

def reduce_graph(graph):
    reduced_graph = []
    for node in graph:
        for nei, cost in graph[node].items():
            reduced_graph.append([node, nei, cost])
    return reduced_graph
