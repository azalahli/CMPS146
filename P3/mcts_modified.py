from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 2000

#this bot will explore the tree more
explore_faction = 100.


#part of selection
#must also return state since its immutable withour return
def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """


    # best node at the moment is the first node and make sure the identity is the identity of the player
    bestNode = node
    #you need this to identify who's who because every other node is anotjer player
    player = identity

    while len(bestNode.untried_actions) == 0 and bestNode.child_nodes != {}:
        #temp best score
        bestScore = -999
        #parent simualtion visits
        result_visit = bestNode.visits
        #where to go if we find a spot
        advance = None

        for child_node in bestNode.child_nodes:

            check = bestNode.child_nodes[child_node]
            win = check.wins / check.visits

            #if other player then 1- win because the success of that node is the complement of yours
            if player != identity:
                win = 1 - win

            #upper confidence bound calculation
            UCB = win + explore_faction * sqrt(log(result_visit) / check.visits)

            if UCB > bestScore:
                bestScore = UCB
                advance = child_node

        bestNode = bestNode.child_nodes[advance]
        state = board.next_state(state, advance)

        #you need to alternate between players because nodes are owned by diifferent people
        player = 1 if player == 2 else 2

    return bestNode, state

    # Hint: return leaf_node


#part of expansion
#must also return state since its immutable
def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.


    """
    # needs to be here to prevent funny python scope error

    #if no untried actions just return as is
    if len(node.untried_actions) == 0:
        return node, state

    what_move = None

    #first see what has not been tried yet
    move = choice(node.untried_actions);

    #doublec check that this move is not in the list of actions that have been tried
    if move not in node.child_nodes.keys():

        #now have that as the node be the one you search
        what_move = move


        if what_move is not None:
            #remove that move from untried actions because now it has been tried
            node.untried_actions.remove(what_move)



    #adds the newNode as a child for the given node
    state = board.next_state(state, what_move)
    # Creates new node with selected move
    # this is the new "child node"
    newNode = MCTSNode(parent=node, parent_action=what_move, action_list=board.legal_actions(state))
    node.child_nodes[what_move] = newNode

    return newNode, state


    # Hint: return new_node

#part of simualtion
#this needs to be changed?
def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """

    #keep the state
    #next state
    #is_ended
    #current player is the winner

    rollout_state = state
    legal = board.legal_actions(rollout_state)

    while legal:
        rollout_move = choice(legal)
        rollout_state = board.next_state(rollout_state, rollout_move)
        legal = board.legal_actions(rollout_state)

    return rollout_state


#this should be correct
def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    # bottom up so not node is not won
    while node != None:

        if won:
            # add win value for all nodes if this leaf won
            node.wins = node.wins +  won
        # all nodes are visited (but not nessasarily won)
        node.visits = node.visits + 1
        # node is now parent
        node = node.parent


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """

    #dont bother with
    identity_of_bot = board.current_player(state)

    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!

        # Selection
        # select a legal move
        # advance to the corresponding child node

        # add to the visit

        leaf, sampled_game = traverse_nodes(node, board, sampled_game, identity_of_bot)

        # Expansion
        # randomly choose one unexpanded move to create the child node corresponding to that move
        # use that child node as the last selected node for thenn selection phase once again

        newNode, sampled_game = expand_leaf(leaf, board, sampled_game)


        #Simulation
            #find all legal games in current game state
            #choose one legal move randomly
            #advance the game state


        sampled_game = rollout(board, sampled_game)


        #check fo the winner before backpropagate
            #updates all nodes for the path visited
        #not sure because hard to read code that isnt commented


        #get the max possible win values
        win = board.win_values(sampled_game)
        won = 0

        #this will see if the current state is a win for the player or not
        if win != None:
            #this will get the win value of the node and add to it
            won = max(win[identity_of_bot], 0)

        #this will add win values to nodes
        backpropagate(newNode, won)

    #this should be changed when it get searched
    bestScore = -999

    #search root node for the best acton for us based on the win rate
    for child_node in root_node.child_nodes:

        check = root_node.child_nodes[child_node]

        if ((check.wins / check.visits) > bestScore) and child_node != None:
            bestScore = (check.wins / check.visits)
            bestAction = child_node

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    # the closer it is to 1, the higher the chance of the bot to win in the next move or the current move
    print("Modified bot picking %s with expected score %f" % (str(bestAction), bestScore))
    return bestAction

