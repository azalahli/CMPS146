from math import inf, sqrt
from heapq import heappop, heappush

def find_path (source_point, destination_point, mesh):
    """
    Searches for a path from source_point to destination_point through the mesh

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:

        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """

    path = []
    #boxes has been split in half to allow both searches to store a position in the "union box"
    forward_boxes = {}
    backward_boxes = {}

    #find the source and destination boxes
    source_box = None
    destination_box = None
    for box in mesh['boxes']: #check each box
        if(source_box and destination_box): #stop checking once we've found both boxes
            break
        if ((source_point[0] >= box[0]) and (source_point[0] <= box[1])): #see if box is our source box
            if((source_point[1] >= box[2]) and (source_point[1] <= box[3])):
                source_box = box
                forward_boxes[source_box] = source_point
        if ((destination_point[0] >= box[0]) and (destination_point[0] <= box[1])): #see if box is our destination box
            if((destination_point[1] >= box[2]) and (destination_point[1] <= box[3])):
                destination_box = box
                backward_boxes[destination_box] = destination_point

    ##################################################

    # The priority queue
    #queue = [(0, source_box, "destination")]
    queue = []
    heappush(queue, (0, source_box, "destination"))
    heappush(queue, (0, destination_box, "source"))

    # The dictionary that will be returned with the costs
    forward_distances = {}
    forward_distances[source_box] = 0
    backward_distances = {}
    backward_distances[destination_box] = 0

    # The dictionary that will store the backpointers
    forward_backpointers = {}
    forward_backpointers[source_box] = None
    backward_backpointers = {}
    backward_backpointers[destination_box] = None

    while queue:
        current_dist, current_node, current_goal = heappop(queue)
        if(current_goal == "destination"):
            current_dist = forward_distances[current_node]
        else:
            current_dist = backward_distances[current_node]

        # Check if we've found a node in common in both searches
        if (is_search_done(current_node, forward_backpointers, backward_backpointers, current_goal)):

            # List containing all cells from initial_position to destination
            box_path = [current_node]
            #box_path = []
            #print("#####START: ", source_point)
            #print("#####END: ", destination_point)
            #print("#####CURRENT NODE: ", current_node)

            # Go backwards from destination until the source using backpointers
            # and add all the nodes in the shortest path into a list
            current_back_node = backward_backpointers[current_node]
            while current_back_node is not None:
                #print("box path",current_back_node)
                box_path.append(current_back_node)
                current_back_node = backward_backpointers[current_back_node]

            path = box_to_lines(destination_point, backward_boxes[current_node], box_path, backward_boxes)

            #print("========================")
            #print(path)

            #box_path.append(current_node)
            box_path = []
            current_back_node = forward_backpointers[current_node]
            while current_back_node is not None:
                box_path.append(current_back_node)
                current_back_node = forward_backpointers[current_back_node]

            source_path = (box_to_lines(source_point, forward_boxes[current_node], box_path, forward_boxes))
            #print("+++++++++++++++++")
            #print(source_path)
            path = path + source_path

            path.append((forward_boxes[current_node], backward_boxes[current_node]))
            break

        # Calculate cost from current note to all the adjacent ones
        #for adj_node, adj_node_cost in adj(graph, current_node):
        adjacents = mesh['adj']
        for adj_node in adjacents[current_node]:
            if current_goal == "source":
                current_point = backward_boxes[current_node]
            else:
                current_point = forward_boxes[current_node]

            if current_point == None:
                current_point = midpoint(current_node)
            adj_node_point = find_legal_move(current_node, adj_node, current_point) #"entry" node into the new box
            adj_node_cost = distance_between_points(current_point, adj_node_point)
            pathcost = current_dist + adj_node_cost

            # If the cost is new
            if current_goal == "source":
                if adj_node not in backward_distances or pathcost < backward_distances[adj_node]:
                    backward_distances[adj_node] = pathcost
                    backward_backpointers[adj_node] = current_node
                    backward_boxes[adj_node] = adj_node_point
                    #push the node to the heap using a heuristic to modify the priority (turning Djikstra's into A*)
                    heappush(queue, ((pathcost + distance_between_points(adj_node_point, source_point)), adj_node, current_goal))
            else:
                if adj_node not in forward_distances or pathcost < forward_distances[adj_node]:
                    forward_distances[adj_node] = pathcost
                    forward_backpointers[adj_node] = current_node
                    forward_boxes[adj_node] = adj_node_point
                    #push the node to the heap using a heuristic to modify the priority (turning Djikstra's into A*)
                    heappush(queue, ((pathcost + distance_between_points(adj_node_point, destination_point)), adj_node, current_goal))

    if not path:
        print("No path found")
    #since I split boxes into forward_boxes and backward_boxes, I need to smash their keys together to return the list
    #of explored boxes
    explored_forward = list(forward_boxes.keys())
    explored_backward = list(backward_boxes.keys())
    return path, (explored_forward + explored_backward)


def box_to_lines(source_point, destination_point, box_path, boxes):
    lines = []
    stop = len(box_path) - 1
    for segment in range(0, stop):
        #print("****lengh: %d, iteration: %d", (((len(box_path)) - 1), segment))
        start_box = box_path[segment]
        end_box = box_path[segment + 1]
        line_start = boxes[start_box]
        line_end = boxes[end_box]
        line = (line_start, line_end)
        lines.append(line)
        #print("~~~~SEGMENT: ",line)#segment)

    #Since we can only link one point per box, the destination point gets overwritten by the "legal" point used to enter
    #its box. Thus, we have to add in that segment manually.
    if(lines):  #make sure lines exists
        lines.append(((lines[0])[0], destination_point))
    else:   #both points in the same box
        lines.append((source_point, destination_point))

    return lines



def midpoint(box):
    #print(box)
    mid_y = (box[0] + box[1])/2
    mid_x = (box[2] + box[3])/2
    mid = (mid_y, mid_x)
    return mid


def find_legal_move(source_box, target_box, current_position):
    #finds a legal line segment connecting your curent position to a point in the box
    #returns a legal point in the target box, plus the distance from the current point to that point
    """
    x1, x2, y1 ,y2
    """
    """
    x_min = max(source_box[0], abs(target_box[0]-source_box[0]))
    x_max = min(source_box[1], abs(target_box[1]-source_box[1]))
    y_min = max(source_box[2], abs(target_box[3]-source_box[2]))
    y_max = min(source_box[3], abs(target_box[2]-source_box[3]))
    """
    x_min = max(source_box[0], target_box[0])
    x_max = min(source_box[1], target_box[1])

    y_min = max(source_box[2], target_box[2])
    y_max = min(source_box[3], target_box[3])

    target_x = 0
    target_y = 0
    if current_position[0] < x_min:
        target_x = x_min
    elif current_position[0] > x_max:
        target_x = x_max
    else:
        target_x = current_position[0]

    if current_position[1] < y_min:
        target_y = y_min
    elif current_position[1] > y_max:
        target_y = y_max
    else:
        target_y = current_position[1]

    return (target_x, target_y)




def distance_between_points(point_1, point_2):
    #returns euclidean distance between two (x,y) points
    distance = sqrt(((abs(point_1[0] - point_2[0])) ** 2) + ((abs(point_1[1] - point_2[1])) ** 2))
    return distance


def is_search_done(current_node, forward_nodes, backward_nodes, direction):
    if direction == "source": #search forward_nodes
        if (current_node in forward_nodes.keys()):
            return True
    elif direction == "destination": # search backward_nodes
        if (current_node in backward_nodes.keys()):
            return True
    else:
        print("WARNING: Invalid direction passed to is_search_done")

    return False
