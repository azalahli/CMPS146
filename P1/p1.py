from p1_support import load_level, show_level, save_level_costs
from math import inf, sqrt
from heapq import heappop, heappush


def dijkstras_shortest_path(initial_position, destination, graph, adj):
    """ Searches for a minimal cost path through a graph using Dijkstra's algorithm.

    Args:
        initial_position: The initial cell from which the path extends.
        destination: The end location for the path.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        If a path exits, return a list containing all cells from initial_position to destination.
        Otherwise, return None.

    """
    """
     function Dijkstra(Graph, source):
2      dist[source] ← 0                           // Initialization
3
4      create vertex set Q
5
6      for each vertex v in Graph:           
7          if v ≠ source
8              dist[v] ← INFINITY                 // Unknown distance from source to v
9          prev[v] ← UNDEFINED                    // Predecessor of v
10
11         Q.add_with_priority(v, dist[v])
12
13
14     while Q is not empty:                      // The main loop
15         u ← Q.extract_min()                    // Remove and return best vertex
16         for each neighbor v of u:              // only v that are still in Q
17             alt ← dist[u] + length(u, v) 
18             if alt < dist[v]
19                 dist[v] ← alt
20                 prev[v] ← u
21                 Q.decrease_priority(v, alt)
22
23     return dist, prev
    """
    dist = {}
    prev = {}
    heapque = [(0, initial_position)]
    neighbor_set = []

    #dist[src] <- 0
    #print(initial_position)
    #heappush(heapque, initial_position)
    dist[initial_position] = 0
    prev[initial_position] = [initial_position]

    # iterate over Q not empty
    # while True:
    # while true would not catch the pathless case
    # while not heapque:
    while heapque:
        path_cost, curr_node = heappop(heapque)
        #print(path_cost, curr_node)
        # if the target is found, break
        if curr_node == destination:
            return (prev[curr_node],path_cost)
        else:
            # neighbor set from adj
            #print(path_cost, curr_node)
            neighbor_set = adj(graph, curr_node)
            #print(neighbor_set)
            for cost, next in neighbor_set:
                #cost, next = neighbor_set
                total_route = cost + path_cost
                # if alt < dist[v]
                """
                if next not in prev or total_route < dist[next]:
                    prev[next].extend(prev[curr_node])
                    prev[next].append(next)
                    dist[next] = path_cost
                """
                if next not in prev:
                    #print(next)
                    prev[next] = []
                    prev[next].extend(prev[curr_node])
                    prev[next].append(next)
                    dist[next] = path_cost
                    heappush(heapque, (total_route, next))
                elif total_route < dist[next]:
                    prev[next].extend(prev[curr_node])
                    prev[next].append(next)
                    dist[next] = path_cost

    return None


def dijkstras_shortest_path_to_all(initial_position, graph, adj):
    """ Calculates the minimum cost to every reachable cell in a graph from the initial_position.

    Args:
        initial_position: The initial cell from which the path extends.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        A dictionary, mapping destination cells to the cost of a path from the initial_position.
    """
    
    dict_every_reachable_cell = {}

    for dest_node in graph['spaces']: #for all cells
        try:
            tuple_temp = dijkstras_shortest_path(initial_position, dest_node, graph, adj)
            dict_every_reachable_cell [dest_node] = tuple_temp[1]
        except TypeError:
            continue
    return dict_every_reachable_cell
    
    #return {1:1}


def navigation_edges(level, cell):
    """ Provides a list of adjacent cells and their respective costs from the given cell.

    Args:
        level: A loaded level, containing walls, spaces, and waypoints.
        cell: A target location.

    Returns:
        A list of tuples containing an adjacent cell's coordinates and the cost of the edge joining it and the
        originating cell.

        E.g. from (0,0):
            [((0,1), 1),
             ((1,0), 1),
             ((1,1), 1.4142135623730951),
             ... ]
    """
    # repurposed from the https://www.redblobgames.com/pathfinding/grids/graphs.html
    dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    result = []
    for dir in dirs:
        #print(cell, dir)
        #print(level['spaces'][cell])
        n_key = (cell[0] + dir[0], cell[1] + dir[1])
        if n_key in level['walls']:
            continue

        #workarounds not needed, but more work to fix than leave comment
        workaround1 = level['spaces'][cell]
        #wall square has no key
        workaround2 = level['spaces'][n_key]
        #print(workaround1)
        dist = 0.5*workaround1+ 0.5*workaround2
        neighbor = [dist, (cell[0] + dir[0], cell[1] + dir[1])]
        #print(neighbor)
        if not n_key in level['walls']:
            result.append(neighbor)

    dirs_di = [[1, 1], [-1, -1], [-1, 1], [1, -1]]
    for dir_di in dirs_di:
        #print(cell, dir)
        #print(level['spaces'][cell])
        n_key = (cell[0] + dir_di[0], cell[1] + dir_di[1])
        if n_key in level['walls']:
            continue
        dist = sqrt(2)*0.5*level['spaces'][cell] + sqrt(2)*0.5*level['spaces'][n_key]
        neighbor = [dist, (cell[0] + dir_di[0], cell[1] + dir_di[1])]
        #print(neighbor)
        if not n_key in level['walls']:
            result.append(neighbor)
    return result


def test_route(filename, src_waypoint, dst_waypoint):
    """ Loads a level, searches for a path between the given waypoints, and displays the result.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        dst_waypoint: The character associated with the destination waypoint.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source and destination coordinates from the level.
    src = level['waypoints'][src_waypoint]
    dst = level['waypoints'][dst_waypoint]

    # Search for and display the path from src to dst.
    path = dijkstras_shortest_path(src, dst, level, navigation_edges)
    if path:
        show_level(level, path[0])
    else:
        print("No path possible!")


def cost_to_all_cells(filename, src_waypoint, output_filename):
    """ Loads a level, calculates the cost to all reachable cells from 
    src_waypoint, then saves the result in a csv file with name output_filename.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        output_filename: The filename for the output csv file.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source coordinates from the level.
    src = level['waypoints'][src_waypoint]

    # Calculate the cost to all reachable cells from src and save to a csv file.
    costs_to_all_cells = dijkstras_shortest_path_to_all(src, level, navigation_edges)
    save_level_costs(level, costs_to_all_cells, output_filename)


if __name__ == '__main__':
    filename, src_waypoint, dst_waypoint = 'test_maze.txt', 'a', 'd'

    # Use this function call to find the route between two waypoints.
    test_route(filename, src_waypoint, dst_waypoint)

    # Use this function to calculate the cost to all reachable cells from an origin point.
    cost_to_all_cells(filename, src_waypoint, 'my_costs.csv')
