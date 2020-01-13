def only_1_planet(state):
    if len(state.my_planets()) == 1:
        return True
    return False

def nearby_threat_check(state):
    my_p = state.my_planets()[0]
    if my_p.num_ships < 110:
        for fleet in state.enemy_fleets():
            if fleet.destination_planet == my_p.ID:
                return True
        for planet in state.enemy_planets():
            if state.distance(my_p.ID, planet.ID) <= 8:
                return True
    return False

def too_many_ships(state):
    for my_p in state.my_planets():
        if my_p.num_ships > 100:
            return True
    return False

def have_50_perc_more_ships(state):
    return sum(planet.num_ships for planet in state.my_planets()) + sum (fleet.num_ships for fleet in state.my_fleets()) >= \
            1.5*(sum(planet.num_ships for planet in state.enemy_planets()) + sum(fleet.num_ships for fleet in state.enemy_fleets()))

def nearby_neutral(state):
    my_planets = state.my_planets()
    neutral_planets = state.neutral_planets()
    
    nearby_neutrals = [planet for planet in neutral_planets if any(state.distance(my_p.ID, planet.ID) <= 11 for my_p in my_planets)]

    if nearby_neutrals:
        return True
    
    return False


def nearby_enemy(state):
    my_planets = state.my_planets()
    enemy_planets = state.enemy_planets()
    
    nearby_enemies = [planet for planet in enemy_planets \
            if any(state.distance(my_p.ID, planet.ID) <= 7 and state.distance(my_p.ID, planet.ID) > 0 for my_p in my_planets)]

    if nearby_enemies:
        return True

    return False

def under_attack(state):
    my_planets = state.my_planets()
    my_fleets = state.my_fleets()
    for fleet in state.enemy_fleets():
        for p in my_planets:
            if p.ID == fleet.destination_planet:
                if any(p.ID == myFleet.destination_planet for myFleet in my_fleets):
                    break
                else:
                    return True
    return False

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def enemy_attacking_neutral(state):
    neutral_planets = state.neutral_planets()
    for fleet in state.enemy_fleets():
            for planet in neutral_planets:
                if planet.ID == fleet.destination_planet:
                    return True
    return False

