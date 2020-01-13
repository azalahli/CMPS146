#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn

# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():

    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')

    lone_planet_plan = Sequence(name='Lone Planet Safety Plan')
    lone_planet_check = Check(only_1_planet)
    in_danger_check = Check(nearby_threat_check)
    do_nothing = Action(stall)
    lone_planet_plan.child_nodes = [lone_planet_check, in_danger_check, do_nothing] 
    
    defense_plan = Sequence(name='Defensive Strategy')
    under_attack_check = Check(under_attack)
    defend = Action(defend_planets_under_attack)
    defense_plan.child_nodes = [under_attack_check, defend]
    
    # need to add another sequence - if i have 1.5x more ships, attack from my highest to their lowest planets
    offense_plan = Selector(name='Offense Strategy 2')

    offense_near = Sequence(name='Attack Close Enemies')
    nearby_enemy_check = Check(nearby_enemy)
    attack_nearby = Action(attack_nearby_enemies)
    offense_near.child_nodes = [nearby_enemy_check, attack_nearby]

    offense_overwhelm = Sequence(name='Attack With Tons of Ships')
    tons_of_ships_check = Check(have_50_perc_more_ships)
    go_ham = Action(attack_weakest_enemy_planets)
    offense_overwhelm.child_nodes = [tons_of_ships_check, go_ham]

    offense_plan.child_nodes = [offense_near, offense_overwhelm]
           
    #need to alter expand to take into account the production rate of the target planets
    expand_plan = Selector(name='Expansion Strategy')

    take_neutrals = Sequence(name='Attack Nearby Neutrals')
    nearby_neutral_check = Check(nearby_neutral)
    take_nearby = Action(take_nearby_neutrals)
    take_neutrals.child_nodes = [nearby_neutral_check, take_nearby]

    use_idle = Sequence(name='Use Idle Ships')
    too_many_ships_check = Check(too_many_ships)
    use_idle_ships = Action(attack_with_idle)
    use_idle.child_nodes = [too_many_ships_check, use_idle_ships]
    
    expand_plan.child_nodes = [take_neutrals, use_idle]
    
    #need to add default plan of redistributing ships from my highest to my lowest
    
    offensive_plan = Sequence(name='Offensive Strategy')
    largest_fleet_check = Check(have_largest_fleet)
    attack = Action(attack_weakest_enemy_planets)
    offensive_plan.child_nodes = [largest_fleet_check, attack]

    spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    spread_action = Action(spread_to_weakest_neutral_planet)
    spread_sequence.child_nodes = [neutral_planet_check, spread_action]

    opportunistic_attack = Sequence(name='Opportunistic Strategy')
    enemy_attacking_n = Check(enemy_attacking_neutral)
    steal_planets = Action(opportunity_attack)
    opportunistic_attack.child_nodes = [enemy_attacking_n, steal_planets]

    #GOOD SECTION
        #PLEASE UTILIZE A BOT FROM THIS SECTION
    #93-114-155-95-88
    #root.child_nodes = [defense_plan, offense_plan, opportunistic_attack, expand_plan]

    #93-118-134-95-99
    root.child_nodes = [lone_planet_plan, spread_sequence, offense_plan, defense_plan, opportunistic_attack, expand_plan]


    #BAD SECTION
        #BOT DIES TO AGGRO
            #DEAD BOT IS BAD
    
    #93-142-LOSS
    #root.child_nodes = [defense_plan, opportunistic_attack, offense_plan, expand_plan, spread_sequence]
    
    #93-124-144-95-88
    #root.child_nodes = [defense_plan, offense_plan, expand_plan, opportunistic_attack, spread_sequence]
    
    #93-124-144-95-88
    #root.child_nodes = [defense_plan, offense_plan, expand_plan, spread_sequence, opportunistic_attack]

    #93-137-LOSS
    #root.child_nodes = [opportunistic_attack, defense_plan, offense_plan, expand_plan, spread_sequence]



    #93-123-LOSS
    #root.child_nodes = [expand_plan, defense_plan, opportunistic_attack, offense_plan, spread_sequence]

    #93-123-LOSS
    #root.child_nodes = [defense_plan, expand_plan, opportunistic_attack, offense_plan, spread_sequence]

    #93-124-LOSS
    #root.child_nodes = [defense_plan, expand_plan, offense_plan,  opportunistic_attack, spread_sequence]
    
    #93-142-LOSS
    #root.child_nodes = [defense_plan, opportunistic_attack, offense_plan, expand_plan, spread_sequence]


    #93-141-148-106-89
    #root.child_nodes = [defense_plan, offense_plan, expand_plan, spread_sequence]
    logging.info('\n' + root.tree_to_string())
    return root

# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
