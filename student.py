# Pedro Miguel Miranda Gonçalves 88859
# Rui Miguel Silva Oliveira 89216
# Pedro Miguel Pinho Silva 89228

import sys
import json
import asyncio
import websockets
import getpass
import os
import math

from mapa import Map
from game import Bomb

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)

        # You can create your own map representation or use the game representation:
        mapa = Map(size=game_properties["size"], mapa=game_properties["map"])

        # Contadores
        reset = 0
        wall_count = 0
        enemy_count = 0
        exit_count = 0
        oneal_count = 0
        count_inicial = 0
        useless = 0
        overtime = 0
        pos_inicial=0
        raio_explosao=4
        length_walls=0

        # Variáveis
        cur_lives = 3
        current_level = 1
        list_1 = []
        list_3 = []
        list_4 = []
        ls_2 = []
        ls_3 = []
        list_99=[]
        new_ls = []
        to_exit = []
        powerup = False
        detonator = False

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )
                if state["lives"] != cur_lives or state["level"] != current_level:
                    wall_count = 0
                    enemy_count = 0
                    exit_count = 0
                    oneal_count = 0
                    overtime = 0
                    list_1 = []
                    list_3 = []
                    list_4 = []
                    ls_2 = []
                    ls_3 = []
                    new_ls = []
                    to_exit = []
                    list_99=[]
                    if state["lives"] != cur_lives:
                        cur_lives -= 1
                    if state["level"] != current_level:
                        current_level += 1
                        powerup = False

                if pos_inicial==0:  #Para evitar o hardcode xD #Funciona
                    if state["bomberman"][0]==1 and state["bomberman"][1]==1:
                        pos_inicial=1
                    else:
                        pos_inicial=2

                if state["enemies"]:
                    enem = closest_enemy(state["bomberman"], state["enemies"])

                if current_level==3 and powerup and not state["powerups"]:
                    detonator=True 
                if current_level==3 and powerup and not state["powerups"]:
                    raio_explosao=5
        
                key = ""
                new_mapa = real_map(mapa.map, state["walls"],state["enemies"])

                
                
                if not state["enemies"] and powerup and state["exit"] and not ls_3 and exit_count == 0:
                    ls_3 = get_exit(state["bomberman"], state["exit"], new_mapa)
                    exit_count = 1

                if state["walls"] or not powerup:
                    lenght_walls_novo=len(state["walls"])
                    if(lenght_walls_novo<length_walls):
                        reset=0
                    length_walls=len(state["walls"])

                    reset += 1
                    if list_4:  
                        list_1 = []
                        wall_count = 0
                        key = list_4.pop(0)
                        
                    elif warning(state["bomberman"],enem) and state["enemies"] and overtime < 50:
                        overtime += 1
                        if same_horizontal(state["bomberman"], enem):
                            list_4 = get_run_horizontal(new_mapa, state["bomberman"], enem, state["enemies"])
                        elif same_vertical(state["bomberman"], enem):
                            list_4 = get_run_vertical(new_mapa, state["bomberman"], enem, state["enemies"])

                    # Prioridade 2: Apanhar o powerup logo que o encontre
                    elif state["powerups"]:
                        ls_2 = get_powerup(state["bomberman"], state["powerups"], new_mapa)
                        powerup = True

                    elif wall_count == 0:
                        overtime = 0 
                        list_1 = destroy_walls(state["bomberman"],state["walls"],new_mapa,state["enemies"],detonator)
                        wall_count = 1
                    elif list_1:
                        key = list_1.pop(0)
                    else:
                        wall_count=0
                    
                        
                elif not state["walls"] and (enem_exists(state["enemies"],["Balloom", "Doll"])):
                    if enemy_count == 0:
                        kill_ls = return_path(new_mapa, state["bomberman"], (1, 4))
                        enemy_count = 1

                    elif enemy_count == 1 and kill_ls:
                        if list_4:
                            kill_ls = []
                            enemy_count=0
                            key = list_4.pop(0)
                        elif warning(state["bomberman"],enem) and state["enemies"]:
                            if same_horizontal(state["bomberman"],enem):
                                list_4 = get_run_horizontal(new_mapa, state["bomberman"], enem, state["enemies"])
                            elif same_vertical(state["bomberman"], enem):
                                list_4 = get_run_vertical(new_mapa, state["bomberman"], enem, state["enemies"])
                        else:
                            key = kill_ls.pop(0)


                    elif state["enemies"] and enemy_count == 1:
                        cycle = corner_killing(state["bomberman"],new_mapa,detonator)
                        enemy_count = 2

                    elif cycle and state["enemies"] and enemy_count == 2:
                        key = cycle.pop(0)
                        if not cycle:
                            enemy_count = 1

                elif not state["walls"] and enem_exists(state["enemies"],["Oneal","Minvo"]):
                    closest_oneal_minvo = get_closest_oneal_minvo_position(state["bomberman"], state["enemies"])
                    closest_name = closest_enemy_name(state["bomberman"], state["enemies"])
                    if closest_name == "Minvo":
                        dist=2
                    elif closest_name == "Oneal":
                        dist=1
                    elif closest_name == "Kondoria":
                        dist=3
                    if oneal_count == 0 and not list_3:
                        if not impossible_oneal_pos(new_mapa, closest_oneal_minvo):
                            new_ls = return_path(new_mapa, state["bomberman"], closest_oneal_minvo)
                            oneal_count = 1

                    elif distance_to_object(state["bomberman"], closest_oneal_minvo) <= dist and oneal_count == 1:
                        key = "B"
                        positions_3 = run(state["bomberman"])
                        run_to2 = get_nearest_spot_oneals(state["bomberman"], closest_oneal_minvo, new_mapa, positions_3)
                        list_3 = return_path(new_mapa, state["bomberman"], run_to2)
                        if not detonator:
                            list_3.extend(["", "", "", "", "", "", "", "", "", "", "", ""])
                        else:
                            list_3.append("A")
                        oneal_count = 0

                    elif list_3:
                        key = list_3.pop(0)

                    elif oneal_count == 1 and new_ls:
                        key = new_ls.pop(0)

                    else:
                        oneal_count = 0
                

                if state["bombs"] and key == "B":
                    key = ""
                
                if ls_2:
                    key = ls_2.pop(0)

                elif ls_3:
                    key = ls_3.pop(0)
                elif reset>=100:
                    list_99=return_path(new_mapa,state["bomberman"],(1,1))
                    list_1=[]
                    reset=0
                elif list_99:
                    key=list_99.pop(0)

                if count_inicial<=300 and state["enemies"] and state["level"]==1:
                    if useless==0:
                        cycle2 = corner_killing_initial()
                        useless=1
                    if useless==1 and cycle2:
                        key = cycle2.pop(0)
                        if not cycle2:
                            useless=0
                    count_inicial+=1
                
                
                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

def safe_place(bombs, bomberman_pos, mapa, radius=5):   #Devolve True se estiver numa posiçao segura para explodir a bomba
    if bombs:
        bomba = Bomb(bombs[0][0],mapa,radius)
        return not bomba.in_range(bomberman_pos)
    else:
        return True

def closest_wall(bomberman_pos, wall_list):
    min_distance = distance_to_object(bomberman_pos, wall_list[0])
    for i in wall_list:
        distance = distance_to_object(bomberman_pos, i)
        if distance <= min_distance:
            min_distance = distance
            min_i = i
    return min_i

def get_powerup(bomberman_pos, powerups, maze):
    powerup_pos = powerups[0][0][0], powerups[0][0][1]
    return return_path(maze, bomberman_pos, powerup_pos)

def get_exit(bomberman_pos, exit, maze):
    exit_pos = exit[0], exit[1]
    return return_path(maze, bomberman_pos, exit_pos)

def destroy_walls(bomberman_pos, wall_list, maze, all_enemies, detonator=False):
    next_wall = closest_wall(bomberman_pos, wall_list)
    positions = position_to_explode_wall(next_wall)
    dif = diference(danger_spots(all_enemies, maze), positions)
    explode_pos = get_nearest_spot(bomberman_pos, maze, dif)
    list_1 = return_path(maze, bomberman_pos, explode_pos)
    list_1.extend(bomb_and_run(explode_pos, maze,detonator))
    return list_1

def bomb_and_run(bomberman_pos, maze, detonator=False):
    # Posições para fugir (tem de ser alterado)
    pos = run(bomberman_pos)
    run_to = get_nearest_spot(bomberman_pos, maze, pos)
    ls = return_path(maze, bomberman_pos, run_to)
    if not detonator:
        ls.extend(["", "", "", "", "", ""])
    else:
        ls.append("A")
    ls.insert(0, "B")
    return ls

def closest_enemy(bomberman_pos, enemies):
    closest = distance_to_object(bomberman_pos, enemies[0]["pos"])
    for e in enemies:
        pos = e["pos"]
        dist = distance_to_object(bomberman_pos, pos)
        if dist <= closest:
            closest = dist
            closest_pos = e["pos"]
    return closest_pos[0], closest_pos[1]

def closest_enemy_name(bomberman_pos, enemies):
    closest = distance_to_object(bomberman_pos, enemies[0]["pos"])
    for e in enemies:
        pos = e["pos"]
        dist = distance_to_object(bomberman_pos, pos)
        if dist <= closest:
            closest = dist
            closest_name = e["name"]
    return closest_name

def impossible_oneal_pos(map, pos):
    ls = [(1, 1), (1, len(map[0]) - 2), (len(map) - 2, 1), (len(map) - 2, len(map[0]) - 2)]
    for p in ls:
        if pos == p:
            return True
    return False

def distance_to_object(obj_1, obj_2):
    distance = math.sqrt(((obj_1[0] - obj_2[0]) ** 2) + ((obj_1[1] - obj_2[1]) ** 2))
    return distance

def warning(bomberman_pos, enem):
    return distance_to_object(bomberman_pos, enem) <= 2

def real_map(map, wall_list,enemies):
    for row in map:
        for index, item in enumerate(row):
            if item == 2:
                row[index] = 0

    if enem_exists(enemies, ["Oneal", "Minvo"])and wall_list == []:
        map[1][1] = 2
        map[1][len(map[0]) - 2] = 2
        map[len(map) - 2][1] = 2
        map[len(map) - 2][len(map[0]) - 2] = 2

    for w in wall_list:
        map[w[0]][w[1]] = 2
    return map

def same_vertical(bomberman_pos, enem):
    return enem[0] == bomberman_pos[0] and bomberman_pos[0] % 2 != 0

def same_horizontal(bomberman_pos, enem):
    return enem[1] == bomberman_pos[1] and bomberman_pos[1] % 2 != 0

def get_run_horizontal(maze, bomberman_pos, enem, allenemies):
    if enem[0] > bomberman_pos[0]:
        positions = run_left(bomberman_pos)
    else:
        positions = run_right(bomberman_pos)
    dif = diference(danger_spots(allenemies, maze),positions)
    run_to = get_nearest_spot(bomberman_pos, maze, dif)
    list_4 = return_path(maze, bomberman_pos, run_to)
    return list_4

def get_run_vertical(maze, bomberman_pos, enem, allenemies):
    if enem[1] > bomberman_pos[1]:
        positions = run_up(bomberman_pos)
    else:
        positions = run_down(bomberman_pos)
    dif = diference(danger_spots(allenemies, maze),positions)
    run_to = get_nearest_spot(bomberman_pos, maze, dif)
    list_4 = return_path(maze, bomberman_pos, run_to)
    return list_4

def danger_spots(enemies,maze):
    ls = []
    if enemies:
        for e in enemies:
            aux = [ 
                   
                    
                  
                    [e["pos"][0]-2,e["pos"][1]+2],
                    [e["pos"][0]-1,e["pos"][1]+2],
                    [e["pos"][0],e["pos"][1]+2],
                    [e["pos"][0]+1,e["pos"][1]+2],
                    [e["pos"][0]+2,e["pos"][1]+2],
                   
                    [e["pos"][0]-2,e["pos"][1]+1],
                    [e["pos"][0]-1,e["pos"][1]+1],
                    [e["pos"][0],e["pos"][1]+1],
                    [e["pos"][0]+1,e["pos"][1]+1],
                    [e["pos"][0]+2,e["pos"][1]+1],
                   
                    [e["pos"][0]-2,e["pos"][1]],
                    [e["pos"][0]-1,e["pos"][1]],
                    [e["pos"][0],e["pos"][1]],
                    [e["pos"][0]+1,e["pos"][1]],
                    [e["pos"][0]+2,e["pos"][1]],
        
                    [e["pos"][0]-2,e["pos"][1]-1],
                    [e["pos"][0]-1,e["pos"][1]-1],
                    [e["pos"][0],e["pos"][1]-1],
                    [e["pos"][0]+1,e["pos"][1]-1],
                    [e["pos"][0]+2,e["pos"][1]-1],
                   
                    [e["pos"][0]-2,e["pos"][1]-2],
                    [e["pos"][0]-1,e["pos"][1]-2],
                    [e["pos"][0],e["pos"][1]-2],
                    [e["pos"][0]+1,e["pos"][1]-2],
                    [e["pos"][0]+2,e["pos"][1]-2],
                    
                  ]

            for spot in aux:
                if spot[0] >= 0 and spot[0] <= len(maze) - 2 and spot[1] >= 0 and spot[1] <= len(maze[0]) - 2 and maze[spot[0]][spot[1]] == 0:
                    ls.append(spot)
    else:
        ls = [(1,1)]
    return ls

def diference(danger, spots):
    danger2 = list(tuple(z) for z in danger)
    danger3 = [t for t in (set(tuple(i) for i in danger2))] 
    intersection = [value for value in danger3 if value in spots]
    for i in spots:
        for j in intersection:
            if i == j:
                spots.remove(i)
    return spots

def run_down(spot):
    ls = [  (spot[0]-1,spot[1]+1),(spot[0]+1,spot[1]+1),
            (spot[0]-2,spot[1]+1),(spot[0]-1,spot[1]+2),(spot[0]+1,spot[1]+2),(spot[0]+2,spot[1]+1),
            (spot[0]-3,spot[1]+1),(spot[0]-2,spot[1]+2),(spot[0]-1,spot[1]+3),(spot[0]+1,spot[1]+3),(spot[0]+2,spot[1]+2),(spot[0]+3,spot[1]+1),
            (spot[0]-5,   ),(spot[0]-4,spot[1]+1),(spot[0]-3,spot[1]+2),(spot[0]-2,spot[1]+3),(spot[0]-1,spot[1]+4),(spot[0]  ,spot[1]+5),(spot[0]+1,spot[1]+4),(spot[0]+2,spot[1]+3),(spot[0]+3,spot[1]+2),(spot[0]+4,spot[1]+1),(spot[0]+5,spot[1]  )
        ]
    return ls

def run_up(spot):
    ls = [  (spot[0]-1,spot[1]-1),(spot[0]+1,spot[1]-1),
            (spot[0]-2,spot[1]-1),(spot[0]-1,spot[1]-2),(spot[0]+1,spot[1]-2),(spot[0]+2,spot[1]-1),
            (spot[0]-3,spot[1]-1),(spot[0]-2,spot[1]-2),(spot[0]-1,spot[1]-3),(spot[0]+1,spot[1]-3),(spot[0]+2,spot[1]-2),(spot[0]+3,spot[1]-1),
            (spot[0]-5,   ),(spot[0]-4,spot[1]-1),(spot[0]-3,spot[1]-2),(spot[0]-2,spot[1]-3),(spot[0]-1,spot[1]-4),(spot[0]  ,spot[1]-5),(spot[0]+1,spot[1]-4),(spot[0]+2,spot[1]-3),(spot[0]+3,spot[1]-2),(spot[0]+4,spot[1]-1),(spot[0]+5,spot[1]  )
        ]
    return ls

def run_right(spot):
    ls = [  (spot[0]+1,spot[1]+1),(spot[0]+1,spot[1]-1),
            (spot[0]+1,spot[1]+2),(spot[0]+1,spot[1]-2),(spot[0]+2,spot[1]+1),(spot[0]+2,spot[1]-1),
            (spot[0]+1,spot[1]+3),(spot[0]+2,spot[1]+2),(spot[0]+3,spot[1]+1),(spot[0]+3,spot[1]-1),(spot[0]+2,spot[1]-2),(spot[0]+1,spot[1]-3),(spot[0]  ,spot[1]-5),
            (spot[0]  ,spot[1]+5),(spot[0]+1,spot[1]+4),(spot[0]+2,spot[1]+3),(spot[0]+3,spot[1]+2),(spot[0]+4,spot[1]+1),(spot[0]+5,spot[1]  ),(spot[0]+4,spot[1]-1),(spot[0]+3,spot[1]-2),(spot[0]+2,spot[1]-3),(spot[0]+1,spot[1]-4),(spot[0],spot[1]-5  )
        ]
    return ls

def run_left(spot):
    ls = [  (spot[0]-1,spot[1]+1),(spot[0]-1,spot[1]-1),
            (spot[0]-1,spot[1]+2),(spot[0]-1,spot[1]-2),(spot[0]-2,spot[1]+1),(spot[0]-2,spot[1]-1),
            (spot[0]-1,spot[1]+3),(spot[0]-2,spot[1]+2),(spot[0]-3,spot[1]+1),(spot[0]-3,spot[1]-1),(spot[0]-2,spot[1]-2),(spot[0]-1,spot[1]-3),(spot[0]  ,spot[1]-5),
            (spot[0]  ,spot[1]+5),(spot[0]-1,spot[1]+4),(spot[0]-2,spot[1]+3),(spot[0]-3,spot[1]+2),(spot[0]-4,spot[1]+1),(spot[0]-5,spot[1]  ),(spot[0]-4,spot[1]-1),(spot[0]-3,spot[1]-2),(spot[0]-2,spot[1]-3),(spot[0]-1,spot[1]-4),(spot[0],spot[1]-5  )
        ]
    return ls

def run(spot):
    ls = [  (spot[0]-1,spot[1]+1),(spot[0]-1,spot[1]-1),(spot[0]+1,spot[1]-1),(spot[0]+1,spot[1]+1),
            (spot[0]-1,spot[1]+2),(spot[0]-2,spot[1]+1),(spot[0]-2,spot[1]-1),(spot[0]-1,spot[1]-2),(spot[0]+1,spot[1]-2),(spot[0]+2,spot[1]-1),(spot[0]+2,spot[1]+1),(spot[0]+1,spot[1]+2),
            (spot[0]-1,spot[1]+3),(spot[0]-2,spot[1]+2),(spot[0]-3,spot[1]+1),(spot[0]-3,spot[1]-1),(spot[0]-2,spot[1]-2),(spot[0]-1,spot[1]-3),(spot[0]+1,spot[1]-3),(spot[0]+2,spot[1]-2),(spot[0]+3,spot[1]-1),(spot[0]+3,spot[1]+1),(spot[0]+2,spot[1]+2),(spot[0]+1,spot[1]+3),
            (spot[0]-4,spot[1]-1),(spot[0]-3,spot[1]-2),(spot[0]-2,spot[1]-3),(spot[0]-1,spot[1]-4),(spot[0]+1,spot[1]-4),(spot[0]+2,spot[1]-3),(spot[0]+3,spot[1]-2),(spot[0]+4,spot[1]-1),
            (spot[0]-4,spot[1]+1),(spot[0]-3,spot[1]+2),(spot[0]-2,spot[1]+3),(spot[0]-1,spot[1]+4),(spot[0]+1,spot[1]+4),(spot[0]+2,spot[1]+3),(spot[0]+3,spot[1]+2),(spot[0]+4,spot[1]+1)
         ]
    return ls


# Retorna os 4 sitios adjacentes à parede
def position_to_explode_wall(wall):
    ls = [(wall[0], wall[1] - 1), (wall[0], wall[1] + 1), (wall[0] - 1, wall[1]), (wall[0] + 1, wall[1])]
    return ls


def get_nearest_spot_oneals(bomberman_pos, oneal_pos, maze, ls):
    if oneal_pos[0] < bomberman_pos[0]:
        for spot in ls:
            if spot[0] >= bomberman_pos[0]:
                if astar(maze, bomberman_pos, spot) != None:
                    return spot
    elif oneal_pos[0] > bomberman_pos[0]:
        for spot in ls:
            if spot[0] <= bomberman_pos[0]:
                if astar(maze, bomberman_pos, spot) != None:
                    return spot
    elif oneal_pos[1] < bomberman_pos[1]:
        for spot in ls:
            if spot[1] >= bomberman_pos[1]:
                if astar(maze, bomberman_pos, spot) != None:
                    return spot
    elif oneal_pos[1] > bomberman_pos[1]:
        for spot in ls:
            if spot[1] <= bomberman_pos[1]:
                if astar(maze, bomberman_pos, spot) != None:
                    return spot
    else:
        for spot in ls:
            if astar(maze, bomberman_pos, spot) != None:
                return spot

def get_nearest_spot(bomberman_pos, maze, ls):
    for spot in ls:
        if spot[0] >= 0 and spot[0] <= len(maze) - 2 and spot[1] >= 0 and spot[1] <= len(maze[0]) - 2 and maze[spot[0]][spot[1]] == 0:
            if astar(maze, bomberman_pos, spot) != None:
                return spot
    return bomberman_pos[0], bomberman_pos[1]

def corner_killing(bomberman_pos,maze,detonator):
    if bomberman_pos[0]!=1 and bomberman_pos[1]!=4:
        return return_path(maze,bomberman_pos,(1,4))
    ls = []
    if not detonator:
        for count in range(0, 14):
            if count == 0:
                ls.append("B")
            elif count == 1:
                ls.append("s")
            elif count == 2:
                ls.append("d")
            elif count == 12:
                ls.append("a")
            elif count == 13:
                ls.append("w")
            else:
                ls.append("")
    if detonator:
        for count in range(0,6):
            if count==0:
                ls.append("B")
            elif count == 1:
                ls.append("s")
            elif count == 2:
                ls.append("d")
            elif count == 3:
                ls.append("A")
            elif count == 4:
                ls.append("a")
            elif count == 5:
                ls.append("w")

    return ls
    
# Código baseado em https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
def astar(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    time = 0
    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:
        time += 1
        if time == 200:
            return None
        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] == 1 or maze[node_position[0]][node_position[1]] == 2:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue


            # Add the child to the open list
            open_list.append(child)

class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

#Esta função retorna uma lista com as keys do caminho desenvolvido pela funçao astar.
#Efetua-se aqui a translação, devolve as keys adequadas
def learn_path(path, ls=[]):
    ponto_x=[]
    ponto_y=[]
    if path!=None:
        if len(path)>1:
            for i,j in path:
                ponto_x.append(i);
                ponto_y.append(j);
            if ponto_x[0]<ponto_x[1]:
                ls.append("d");
            elif ponto_x[0]>ponto_x[1]:
                ls.append("a");
            elif ponto_y[0]<ponto_y[1]:
                ls.append("s");
            elif ponto_y[0]>ponto_y[1]:
                ls.append("w");
            path.pop(0)
            return learn_path(path,ls)
    else:
        ls.append("")
    return ls

def return_path(maze,start,end):    #Apenas serve para simplificar a main
    path=astar(maze,start,end)
    list=[]
    return learn_path(path,list)

def enem_exists(enemies, enem_name):
    exists=False
    for i in enemies:
        for j in enem_name:
            if i["name"] == j:
                exists=True
    return exists

def get_closest_oneal_minvo_position(bomberman_pos, enemies):
    valor_retorno = None
    if enem_exists(enemies, ["Oneal", "Minvo"]):
        min = 1000
        for i in enemies:
            position = i["pos"]
            name = i["name"]
            distancia = distance_to_object(bomberman_pos, position);
            if(distancia < min and name == 'Oneal' or name == 'Minvo'):
                min = distancia
                valor_retorno = position
    return valor_retorno[0], valor_retorno[1]

def get_powerup_position(powerups):
    if powerups:
        return powerups[0][0][0],powerups[0][0][1]
    else:
        return None

def corner_killing_initial():
    ls=[]
    for count in range(0, 10):
            if count == 0:
                ls.append("d")
            elif count == 1:
                ls.append("B")
            elif count == 2:
                ls.append("a")
            elif count == 3:
                ls.append("s")
            elif count == 9:
                ls.append("w")
            else:
                ls.append("")
    return ls

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
