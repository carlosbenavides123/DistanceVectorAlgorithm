import collections

# the packet data is src_nei_vector (neighbor vector in form of a dictionary)
# i.e. { <neighbor_node_id>: {neighbor_neighbor_node1: cost, neighbor_neighbor_node2: cost, neighbor_neighbor_node3: cost}}
def update_routing_table(graph, src_server_id, src_nei_vector, parents):
    # print(graph, src_server_id, src_nei_vector, parents)
    src_nei_key = None
    for key in src_nei_vector:
        src_nei_key = key
    if src_nei_key == None:
        # raise error
        return graph, parents

    # own server vector {1: {2: 1}}
    # neighbor server vector {2: {1: 2}} -> update to {2: {1: 1}}
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
        if src_server_id in src_nei_vector[src_nei_key]:
            src_to_nei_cost = src_nei_vector[src_nei_key][src_server_id]
            parents[src_nei_key-1] = src_nei_key
        if src_to_nei_cost == float("inf"):
            # raise error
            print("error src_to_nei_cost float inf")
            print("DEBUG src_vector", src_vector)
            print("DEBUG nei_vector", src_nei_vector)
            return graph, parents, True

    src_vector_keys = set([key for key in src_vector])

    # algorithm
    for nei_nei_node, nei_nei_cost in nei_vector.items():
        if nei_nei_node == src_server_id:
            continue

        # own server {1: {2: 1}}
        # nei {2: {1:1, {3: 1}}}
        # -> {1: {2: 1, 3: 2}}
        if nei_nei_node not in src_vector_keys:
            new_min_src_vector[nei_nei_node] = nei_nei_cost + src_to_nei_cost
            parents[nei_nei_node-1] = src_nei_key
        else:
            # a different example
            # own server vector {1: {2: 5, 3: 10}}
            # neighbor vector {2: {1: 5, 3: 3}}
            # cheaper path to 3 from 1 is to go to server node 2 then server node 3 ( cost 5 + 3 )
            # updating server_node 1 to be {1: {2: 5, 3: 8}}
            for src_vector_nei, src_vector_nei_cost in src_vector.items():
                if src_vector_nei == nei_nei_node:
                    if src_vector_nei_cost > nei_nei_cost + src_to_nei_cost:
                        new_min_src_vector[src_vector_nei] = nei_nei_cost + src_to_nei_cost
                        parents[nei_nei_node-1] = src_nei_key
                    else:
                        new_min_src_vector[src_vector_nei] = src_vector_nei_cost
                    break
    # new_min_src_vector = merge_two_dicts(src_vector, new_min_src_vector)
    graph[src_server_id] = new_min_src_vector
    graph[src_nei_key] = nei_vector
    # print(graph)
    return graph, parents, False

