import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.
    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        # if rule.get('Consumes')[item] == state:
        # """
        # print("state")
        # print(state)
        """
False
state
{'Produces': {'coal': 1}, 'Requires': {'wooden_pickaxe': True}, 'Time': 4}
needs edge protector
        """
        if rule.get('Consumes') is not None:
            for cons in rule.get('Consumes'):
                # print(cons)
                # this is valid because we know we have a dict
                req = rule.get('Consumes')[cons]
                if state.get(cons, 0) < req:
                    return False
        # """
        if rule.get('Requires') is not None:
            for cons in rule.get('Requires'):
                # print(cons)
                # this is valid because we know we have a dict
                req = rule.get('Requires')[cons]
                # print("REQUIREMENT")
                # print(req)
                # just needs the one
                # print("TOOLREQ")
                # print(state.get(cons))
                # print(req)
                #print(state.get(cons, 0) > 0 and req is True)
                if state.get(cons, 0) < 1 and req is True:
                    #print("this should probably not show")
                    return False

        return True

    # print(check(rule))
    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        next_state = state.copy()
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        if rule.get('Produces') is not None:
            for res in rule.get('Produces'):
                next_state[res] = next_state[res] + rule.get('Produces')[res]

        if rule.get('Consumes') is not None:
            for con in rule.get('Consumes'):
                next_state[con] = next_state[con] - rule.get('Consumes')[con]

        #next_state = None
        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        if goal is not None:
            for item in goal:
                if state.get(item) < goal.get(item):
                    return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state, act, dead_list):
    #arbitrarily large number
    ALN = 10000000
    PRIORITY = 0
    DEFAULT = 5
    ORE_SORCERY = -10
    MELTING_SORCERY = -20
    CUT_WITH_AXE = 3

    #this doesn't work anyways
    #if state['iron_axe'] >= 1 and "for wood" in act:
    #    return CUT_WITH_AXE

    #if state['iron_pickaxe'] >= 1 and (act == "craft wooden_pickaxe at bench" or act == "craft stone_pickaxe at bench"):
    #The rationale is that with a higher tier tool you wish to discourage using or making lower ones
    if state['bench'] >= 1 and act == "craft bench":
        print("repeat bench block")
        dead_list.append(act)
        return ALN
    if state['furnace'] >= 1 and act == "craft furnace at bench":
        print("repeat furnace block")
        dead_list.append(act)
        return ALN
    
    if state['iron_pickaxe'] >= 1 and act == "craft iron_pickaxe at bench":
        print("repeat iron p block")
        dead_list.append(act)
        return ALN
    if state['iron_axe'] >= 1 and act == "craft iron_axe at bench":
        print("repeat iron a block")
        dead_list.append(act)
        return ALN
    if state['stone_pickaxe'] >= 1 and act == "craft stone_pickaxe at bench":
        print("repeat s p block")
        dead_list.append(act)
        return ALN
    if state['stone_axe'] >= 1 and act == "craft stone_axe at bench":
        print("repeat s a block")
        dead_list.append(act)
        return ALN
    if state['wooden_pickaxe'] >= 1 and act == "craft wooden_pickaxe at bench":
        print("repeat w p block")
        dead_list.append(act)
        return ALN
    if state['wooden_axe'] >= 1 and act == "craft wooden_axe at bench":
        print("repeat w a block")
        dead_list.append(act)
        return ALN

    if state['iron_pickaxe'] >= 1 and ("wooden_pickaxe" in act or "stone_pickaxe" in act):
        print("INF stone pick block")
        dead_list.append(act)
        return ALN
    if state['iron_axe'] >= 1 and ("wooden_axe" in act or "stone_axe" in act):
        print("INF stone axe block")
        dead_list.append(act)
        return ALN
    if state['stone_pickaxe'] >= 1 and ("wooden_pickaxe" in act):
        print("INF wood pick block")
        dead_list.append(act)
        return ALN
    if state['stone_axe'] >= 1 and ("wooden_axe" in act):
        print("INF wood axe block")
        dead_list.append(act)
        return ALN
    
    if state['iron_pickaxe'] < 1 and act == "craft iron_pickaxe at bench" and not act in dead_list:
        print("PRIO iron p")
        dead_list.append(act)
        return PRIORITY
    if state['iron_axe'] < 1 and act == "craft iron_axe at bench" and not act in dead_list:
        print("PRIO iron a")
        #dead_list.append(act)
        return PRIORITY
    if state['stone_pickaxe'] < 1 and act == "craft stone_pickaxe at bench" and not act in dead_list:
        print("PRIO s p ")
        dead_list.append(act)
        return PRIORITY
    if state['stone_axe'] < 1 and act == "craft stone_axe at bench" and not act in dead_list:
        print("PRIO s a")
        dead_list.append(act)
        return PRIORITY
    if state['wooden_pickaxe'] < 1 and act == "craft wooden_pickaxe at bench" and not act in dead_list:
        print("PRIO w p")
        dead_list.append(act)
        return PRIORITY
    #wooden axe not useful ever
    """
    if state['wooden_axe'] < 1 and act == "craft wooden_axe at bench" and not act in dead_list:
        print("PRIO w a")
        dead_list.append(act)
        return PRIORITY
    """
    if act == "smelt ore in furnace" and state['ingot'] < 6:
        #print("smelt the damn ore")
        return MELTING_SORCERY
    if "ore" in act and (state['ore'] + state['ingot']) < 3:
        #print("ore prio")
        return ORE_SORCERY
    if state['cart'] >= 1 and act == "craft cart at bench":
        dead_list.append(act)
        return ALN

    #print("default")
    #any way to avoid calling this?
    return DEFAULT


def search(graph, state, is_goal, limit, heuristic):
    start_time = time()

    heapqueue = [(0, state)]
    
    dist = {}
    prev = {}
    actions = {}

    dist[state] = 0
    prev[state] = None
    actions[state] = None

    cut_copies = [state]
    dead_list = []

    neighbor_set = []

    #costInTime = 0
    
    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while (time() - start_time < limit) and heapqueue:
        path_cost, curr_state = heappop(heapqueue)

        if is_goal(curr_state):
            final_path = [(curr_state, actions[curr_state])]
            #print(prev.get(curr_state))
            best_result = prev.get(curr_state)
            #reverse the action/result list
            while best_result is not None:
                final_path.append((best_result, actions[best_result]))
                best_result = prev[best_result]
            final_path.reverse()
            print('states visited: ')
            print(len(cut_copies))
            print('actions: ')
            print(len(final_path))
            print(time() - start_time, "seconds.")
            return final_path

        neighbor_set = graph(curr_state)
        for r in neighbor_set:
            act = r[0]
            next = r[1]
            next_cost = r[2]
            if not act in dead_list:
                #print(dead_list)
                #route = path_cost + next_cost
                total_route = path_cost + next_cost + heuristic(curr_state, act, dead_list)
                #print("next")
                #print(next)
                #print(act)
                if next not in dist or total_route < dist[next] and next not in cut_copies:
                    
                    prev[next] = curr_state
                    dist[next] =  total_route
                    actions[next] = act

                    cut_copies.append(next)
                    heappush(heapqueue, (total_route, next))
    """
    #jay's stuff
    dist = {}
    prev = {}       #Dictionaries dont do much 
    prev[state] = 0 #I think we use this instead
    heapque = [(0, state)]
    cost = {}
    neighbor_set = []
    list_of_actions = []

    dist[state] = 0
    return_tuples = None
    start_time = time()
    #imported code from myron p's P1
    #and possibly p2 soonTM

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit:
        
        while heapque:
            path_cost, curr_state = heappop(heapque)

            if is_goal(curr_state):
                path = [(curr_state, dist[curr_state])]

                curr_prev_state = prev[curr_state]

                return path

            else:
                neighbor_set = graph(curr_state)
                #refactor to use time inside json file for cost
                for r in neighbor_set:
                    total_route = r[2] + path_cost #+heuristic
                    #print(r[0])
                    #print(r[1])
                    #print(r[2])
                    name_of_action = r[0]
                    next = r[1]
                    if next not in prev or total_route < r[2] and r[2] not in visited:
                        print("CURR")
                        print(curr_state)
                        print(total_route)
                        print(name_of_action)
                        dist[next] = total_route
                        #print("NEW")
                        #print(r[1])
                        list_of_actions.append(name_of_action)

                        #print(next)
                        #prev[next].extend(prev[curr_node])
                        prev[next] = curr_state
                        #nextState, cost = effect(state)
                        heappush(heapque, (total_route, next))
    """
    # Failed to find a path
    #print the final state to see what the fk is going on
    print(heapqueue[0])
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None
    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None


if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    print('Goal:', Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    print('Example recipe:', 'craft stone_pickaxe at bench ->',
          Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])
    #print(is_goal)

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        cost = 0
        for state, action in resulting_plan:
            if action:
                cost += Crafting['Recipes'][action]['Time']
            print('\t', state)
            print(action)
        print('[cost=' + str(cost) + ', len=' + str(len(resulting_plan)) + ']')
