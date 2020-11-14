import collections

def bellman_ford(graph, src):
    n = len(graph)
    dist = n * [float("inf")]
    dist[src-1] = 0

    reduced_graph = reduce_graph(graph)

    for _ in range(n):
        new_dist = dist[:]
        for u, v, w in reduced_graph:
            new_dist[v-1] = min(new_dist[v-1], dist[u-1] + w)
        if new_dist == dist:
            break
        dist = new_dist

    for key in graph:
        if key == src:
            graph[src] = []
            for idx, cost in enumerate(dist):
                if idx + 1 == src:
                    continue
                graph[src].append((idx + 1, cost))
        else:
            updated_nei_list = [(nei, cost) for nei, cost in graph[key] if nei != src]
            updated_nei_list.append((src, new_dist[key-1]))
            graph[key] = updated_nei_list
    return graph

def reduce_graph(graph):
    reduced_graph = []
    for node in graph:
        for nei, cost in graph[node]:
            reduced_graph.append([node, nei, cost])
    return reduced_graph
