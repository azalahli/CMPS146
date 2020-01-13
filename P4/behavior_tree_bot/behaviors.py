import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def stall(state):
    return True

def attack_with_idle(state):
    attacked = False
    for my_p in state.my_planets():
        if my_p.num_ships > 100:
            for other_p in state.not_my_planets():
                if other_p.growth_rate >= 3:
                    need = other_p.num_ships + 1
                    if other_p in state.enemy_planets():
                        need += other_p.growth_rate * state.distance(my_p.ID, other_p.ID)
                    if my_p.num_ships > need:
                        issue_order(state, my_p.ID, other_p.ID, need)
                        attacked = True
    return attacked 

def take_nearby_neutrals(state):
    my_planets = state.my_planets()
    my_fleets = state.my_fleets()
    neutral_planets = state.neutral_planets()
    enemy_fleets = state.enemy_fleets()
    attacked = False 

    for neutral_p in neutral_planets:
        if neutral_p.growth_rate < 3:
            continue
        if any(neutral_p.ID == my_fleet.destination_planet for my_fleet in my_fleets):
            continue
        need = neutral_p.num_ships + 1
        for my_p in my_planets:
            if any(enemy_fleet.destination_planet == my_p.ID for enemy_fleet in enemy_fleets):
                continue
            if my_p.num_ships >= need and state.distance(my_p.ID, neutral_p.ID) <= 11:
                attacked = issue_order(state, my_p.ID, neutral_p.ID, need)
                break

    return False 

def attack_nearby_enemies(state):
    my_planets = state.my_planets()
    my_fleets = state.my_fleets()
    enemy_planets = state.enemy_planets()
    enemy_fleets = state.enemy_fleets()
    attacked = False

    for enemy_p in enemy_planets:
        for my_p in my_planets:
            dist = state.distance(my_p.ID, enemy_p.ID)
            
            if dist <= 8:
                need = enemy_p.num_ships + enemy_p.growth_rate*dist + 1
                if my_p.num_ships > need:
                    if any(my_p.ID == enem_fleet.destination_planet for enem_fleet in enemy_fleets):
                        continue
                    else:
                        issue_order(state, my_p.ID, enemy_p.ID, need)
                        attacked = True
                        break 
            
    return attacked 


def defend_planets_under_attack(state):
    my_planets = [planet for planet in state.my_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    my_fleets= state.my_fleets()
    enemy_fleets = state.enemy_fleets()
    
    # tracks every planet that has an incoming enemy fleet
    under_attack = []
    for fleet in enemy_fleets:
        for planet in my_planets:
            if planet.growth_rate < 3:
                continue
            if planet.ID == fleet.destination_planet:
                under_attack.append((fleet, planet))

    # for every planet under attack, if there are not already enough reinforcements, send more
    for fleet, planet in under_attack:
        # calculate if there are already enough reinforcements
        incoming = fleet.num_ships
        have = fleet.turns_remaining * planet.growth_rate + planet.num_ships
        reinforcements = sum(my_fleet.num_ships for my_fleet in my_fleets if my_fleet.destination_planet == planet.ID)
        need = incoming - (have + reinforcements) + 1
        
        reinforce_planet = []
        # send reinforcements from the closest available planet
        if need > 0:
            for source_p in my_planets:
                if source_p.ID != planet.ID and source_p not in under_attack and source_p.num_ships > need:
                    if state.distance(source_p.ID, planet.ID) <= state.distance(fleet.source_planet, planet.ID):
                        #issue_order(state, source_p.ID, planet.ID, need)
                        reinforce_planet.append(source_p.ID)
                        break
        #"""
        for help in reinforce_planet:
            issue_order(state, help, planet.ID, need / len(reinforce_planet))
        #"""
    # if we defend, we still want to attack?
    return False

def attack_weakest_enemy_planets(state):
    #"""
    my_planets = [planet for planet in state.my_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    #"""
    enemy_planets = state.enemy_planets()
    enemy_fleets = state.enemy_fleets()
    
    sorted_planets = iter(sorted(my_planets, key=lambda t: t.num_ships, reverse=True))
    weakest_planets = iter(sorted(enemy_planets, key=lambda t: t.num_ships))
    
    attacked = False 

    try:
        strongest_p = next(sorted_planets)
        weakest_p = next(weakest_planets)
         
        while True:
            need = weakest_p.num_ships + weakest_p.growth_rate*state.distance(strongest_p.ID, weakest_p.ID) + 1
            attacked = issue_order(state, strongest_p.ID, weakest_p.ID, need)
            weakest_p = next(weakest_planets)
             
        return attacked
        
    except StopIteration:
        return attacked 

def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, weakest_planet.num_ships + 1)


def opportunity_attack(state):
    my_planets = state.my_planets()
    #enemy_planets = state.enemy_planets()
    neutral_planets = [planet for planet in state.neutral_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_fleets = state.enemy_fleets()
    my_fleets = state.my_fleets()
    
    sorted_planets = iter(sorted(my_planets, key=lambda t: t.num_ships, reverse=True))
    #logically speaking, attack_weakest_enemy_planet attacks the enemy planet 
    #also, the *closest* weakest enemy planet will be the weakest neutral one
    #immediately after an enemy invasion, assuming that neutrals are interspesed
    #evenly
    
    attacked = False
    under_attack = []
    for fleet in enemy_fleets:
        for planet in neutral_planets:
            if planet.growth_rate < 3:
                continue
            if planet.ID == fleet.destination_planet:
                under_attack.append((fleet, planet))


    try:
        strongest_p = next(sorted_planets)
    except StopIteration:
        return False
    # for every neutral planet under attack, parse
    for fleet, planet in under_attack:
        # calculate remaining ships
        attackers = fleet.num_ships
        neutral_defenders = planet.num_ships
        remainder = attackers - neutral_defenders
        projected_defenders = remainder + planet.growth_rate*state.distance(strongest_p.ID, planet.ID)
        #remainder += planet.growth_rate * fleet.turns_remaining

        
        # if remaining ships is less than strongest, steal em
        if projected_defenders < strongest_p.num_ships + 1:
            issue_order(state, strongest_p.ID, planet.ID, projected_defenders + 3)
            attacked = True

  
    # if we defend, we still want to attack?
    return attacked 
