import collections

# def merge_two_dicts(x, y):
#     z = x.copy()   # start with x's keys and values
#     z.update(y)    # modifies z with y's keys and values & returns None
#     return z

def update_routing_table(graph, src_server_id, src_nei_vector, parents):
    # print(graph, src_server_id, src_nei_vector, parents)
    src_nei_key = None
    for key in src_nei_vector:
        src_nei_key = key
    if src_nei_key == None:
        # raise error
        return graph, parents
    if src_nei_key in graph[src_server_id] and src_server_id in src_nei_vector[src_nei_key]:
        graph[src_server_id].update({src_nei_key: 
                min(graph[src_server_id][src_nei_key], src_nei_vector[src_nei_key][src_server_id])
            })
    nei_vector = src_nei_vector[src_nei_key]
    src_vector = graph[src_server_id].copy()
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
            return graph, parents
    src_vector_keys = set([key for key in src_vector])

    for nei_nei_node, nei_nei_cost in nei_vector.items():
        if nei_nei_node == src_server_id:
            continue

        if nei_nei_node not in src_vector_keys:
            new_min_src_vector[nei_nei_node] = nei_nei_cost + src_to_nei_cost
            parents[src_nei_key-1] = src_nei_key
        else:
            for src_vector_nei, src_vector_nei_cost in src_vector.items():
                if src_vector_nei == nei_nei_node:
                    if src_vector_nei_cost > nei_nei_cost + src_to_nei_cost:
                        new_min_src_vector[src_vector_nei] = nei_nei_cost + src_to_nei_cost
                        parents[src_nei_key-1] = src_nei_key
                    else:
                        new_min_src_vector[src_vector_nei] = src_vector_nei_cost
                    break
    print(5)
    # new_min_src_vector = merge_two_dicts(src_vector, new_min_src_vector)
    graph[src_server_id] = new_min_src_vector
    graph[src_nei_key] = nei_vector
    # return graph, parents
    return bellman_ford(graph, src_server_id), parents

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
    return graph

def reduce_graph(graph):
    reduced_graph = []
    for node in graph:
        for nei, cost in graph[node].items():
            reduced_graph.append([node, nei, cost])
    return reduced_graph

def recompute_graph_with_fallback(src_server_id, deleted_nodes, fallback_graph):
    for node in deleted_nodes:
        if node in fallback_graph and src_server_id in fallback_graph[node]:
            del fallback_graph[node][src_server_id]
        if src_server_id in fallback_graph and node in fallback_graph[src_server_id]:
            del fallback_graph[src_server_id][node]

    parents = [] * 4
    new_graph = {}

    return new_graph, parents
