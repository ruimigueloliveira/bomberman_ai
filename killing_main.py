import sys
import json
import asyncio
import websockets
import getpass
import os
import math

from mapa import Map

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)

        mapa = Map(size=game_properties["size"], mapa=game_properties["map"])

        count = 0

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )

                key = ""
                new_mapa = real_map(mapa.map, state["walls"])

                enem = closest_enemie(state["bomberman"], state["enemies"])
                position = enem["pos"]
                distance = distance_to_object(state["bomberman"], position)

                if distance < 6:
                    
                    # print("distance: ", distance)
        
                    if count == 0:
                        print("quero por bomba")
                        if enem["pos"][0] == state["bomberman"][0] and state["bomberman"][1] % 2 != 0:
                            print("mesma coluna")

                            if enem["pos"][1] > state["bomberman"][1]:
                                positions = run_vertical_up(state["bomberman"])
                                

                            elif enem["pos"][1] < state["bomberman"][1]:
                                positions = run_vertical_down(state["bomberman"])
                        
                            key = "B"
                            run_to = get_nearest_spot(state["bomberman"], new_mapa, positions)
                            print("posicao atual: ", state["bomberman"])
                            print("alvo: ", run_to)
                            path = astar(new_mapa, state["bomberman"], run_to)
                            list_2 = learn_path(path) 
                            print("caminho em keys")
                            list_2.reverse()
                            count = 1
                            print("list: ",list_2)
                            
                                    
                        elif enem["pos"][1] == state["bomberman"][1] and state["bomberman"][1] % 2 != 0:
                            print("mesma linha")

                            if enem["pos"][0] > state["bomberman"][0]:
                                positions = run_horizontal_left(state["bomberman"])
                                

                            elif enem["pos"][0] < state["bomberman"][0]:
                                positions = run_horizontal_right(state["bomberman"])

                            key = "B"
                            run_to = get_nearest_spot(state["bomberman"], new_mapa, positions)
                            print("posicao atual: ", state["bomberman"])
                            print("alvo: ", run_to)
                            path = astar(new_mapa, state["bomberman"], run_to)
                            list_2 = learn_path(path) 
                            print("caminho em keys")
                            list_2.reverse()
                            count = 1
                            print("list: ",list_2)
                                
                        else:
                            print("obliquo")
                            list_2 = [""]
                            count = 1
                            print("list: ",list_2)
                            
                    elif list_2 and count == 1:
                        print("bombando")
                        key = list_2.pop()
                        print("key", key)
                        
                    elif not list_2 and count == 1:
                        print("reseting")
                        count = 0
                        key = ""

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

def run_vertical_down(spot):
    # (x-,y+) and (x+,y+)
    print("run_vertical_down")
    ls = [ (spot[0]-1,spot[1]+1),
       (spot[0]-2,spot[1]+1),(spot[0]-1,spot[1]+2),
       (spot[0]-3,spot[1]+1),(spot[0]-2,spot[1]+2),(spot[0]-1,spot[1]+3),
       (spot[0]-4,spot[1]+1),
       (spot[0]-4,spot[1]+2),(spot[0]-3,spot[1]+2),
       (spot[0]-4,spot[1]+3),(spot[0]-3,spot[1]+3),(spot[0]-2,spot[1]+3),
       (spot[0]-4,spot[1]+4),(spot[0]-3,spot[1]+4),(spot[0]-2,spot[1]+4),(spot[0]-1,spot[1]+4),
       (spot[0]+1,spot[1]+1),
       (spot[0]+2,spot[1]+1),(spot[0]+1,spot[1]+2),
       (spot[0]+3,spot[1]+1),(spot[0]+2,spot[1]+2),(spot[0]+1,spot[1]+3),
       (spot[0]+4,spot[1]+1),
       (spot[0]+4,spot[1]+2),(spot[0]+3,spot[1]+2),
       (spot[0]+4,spot[1]+3),(spot[0]+3,spot[1]+3),(spot[0]+2,spot[1]+3),
       (spot[0]+4,spot[1]+4),(spot[0]+3,spot[1]+4),(spot[0]+2,spot[1]+4),(spot[0]+1,spot[1]+4),
       (spot[0]  ,spot[1]+4),(spot[0]+4,spot[1]  ),(spot[0]-4,spot[1]  ) 
     ]

    return ls

def run_vertical_up(spot):
    # (x-,y-) and (x+,y-)
    print("run_vertical_up")
    ls = [ (spot[0]-1,spot[1]-1),
       (spot[0]-2,spot[1]-1),(spot[0]-1,spot[1]-2),
       (spot[0]-3,spot[1]-1),(spot[0]-2,spot[1]-2),(spot[0]-1,spot[1]-3),
       (spot[0]-4,spot[1]-1),
       (spot[0]-4,spot[1]-2),(spot[0]-3,spot[1]-2),
       (spot[0]-4,spot[1]-3),(spot[0]-3,spot[1]-3),(spot[0]-2,spot[1]-3),
       (spot[0]-4,spot[1]-4),(spot[0]-3,spot[1]-4),(spot[0]-2,spot[1]-4),(spot[0]-1,spot[1]-4),
       (spot[0]  ,spot[1]-4),(spot[0]+4,spot[1]  ),(spot[0]-4,spot[1]  ),
       (spot[0]+1,spot[1]-1),
       (spot[0]+2,spot[1]-1),(spot[0]+1,spot[1]-2),
       (spot[0]+3,spot[1]-1),(spot[0]+2,spot[1]-2),(spot[0]+1,spot[1]-3),
       (spot[0]+4,spot[1]-1),
       (spot[0]+4,spot[1]-2),(spot[0]+3,spot[1]-2),
       (spot[0]+4,spot[1]-3),(spot[0]+3,spot[1]-3),(spot[0]+2,spot[1]-3),
       (spot[0]+4,spot[1]-4),(spot[0]+3,spot[1]-4),(spot[0]+2,spot[1]-4),(spot[0]+1,spot[1]-4)  
     ]
    return ls

def run_horizontal_right(spot):
    # (x+,y-) and (x+,y+)
    print("run_horizontal_right")
    ls = [ (spot[0]+1,spot[1]-1),
       (spot[0]+2,spot[1]-1),(spot[0]+1,spot[1]-2),
       (spot[0]+3,spot[1]-1),(spot[0]+2,spot[1]-2),(spot[0]+1,spot[1]-3),
       (spot[0]+4,spot[1]-1),
       (spot[0]+4,spot[1]-2),(spot[0]+3,spot[1]-2),
       (spot[0]+4,spot[1]-3),(spot[0]+3,spot[1]-3),(spot[0]+2,spot[1]-3),
       (spot[0]+4,spot[1]-4),(spot[0]+3,spot[1]-4),(spot[0]+2,spot[1]-4),(spot[0]+1,spot[1]-4),
       (spot[0]+0,spot[1]+4),(spot[0]+0,spot[1]+4),(spot[0]+0,spot[1]-4),
       (spot[0]+1,spot[1]+1),
       (spot[0]+2,spot[1]+1),(spot[0]+1,spot[1]+2),
       (spot[0]+3,spot[1]+1),(spot[0]+2,spot[1]+2),(spot[0]+1,spot[1]+3),
       (spot[0]+4,spot[1]+1),
       (spot[0]+4,spot[1]+2),(spot[0]+3,spot[1]+2),
       (spot[0]+4,spot[1]+3),(spot[0]+3,spot[1]+3),(spot[0]+2,spot[1]+3),
       (spot[0]+4,spot[1]+4),(spot[0]+3,spot[1]+4),(spot[0]+2,spot[1]+4),(spot[0]+1,spot[1]+4)  
     ]
    return ls

def run_horizontal_left(spot):
    print("run_horizontal_left")
    # (x-,y-) and (x-,y+)
    ls = [ (spot[0]-1,spot[1]-1),
       (spot[0]-2,spot[1]-1),(spot[0]-1,spot[1]-2),
       (spot[0]-3,spot[1]-1),(spot[0]-2,spot[1]-2),(spot[0]-1,spot[1]-3),
       (spot[0]-4,spot[1]-1),
       (spot[0]-4,spot[1]-2),(spot[0]-3,spot[1]-2),
       (spot[0]-4,spot[1]-3),(spot[0]-3,spot[1]-3),(spot[0]-2,spot[1]-3),
       (spot[0]-4,spot[1]-4),(spot[0]-3,spot[1]-4),(spot[0]-2,spot[1]-4),(spot[0]-1,spot[1]-4),
       (spot[0]-4,spot[1]),(spot[0],spot[1]+4),(spot[0],spot[1]-4),
       (spot[0]-1,spot[1]+1),
       (spot[0]-2,spot[1]+1),(spot[0]-1,spot[1]+2),
       (spot[0]-3,spot[1]+1),(spot[0]-2,spot[1]+2),(spot[0]-1,spot[1]+3),
       (spot[0]-4,spot[1]+1),
       (spot[0]-4,spot[1]+2),(spot[0]-3,spot[1]+2),
       (spot[0]-4,spot[1]+3),(spot[0]-3,spot[1]+3),(spot[0]-2,spot[1]+3),
       (spot[0]-4,spot[1]+4),(spot[0]-3,spot[1]+4),(spot[0]-2,spot[1]+4),(spot[0]-1,spot[1]+4)
     ]
    return ls

def closest_enemie(bomberman_pos, enemie):
    min_distance = distance_to_object(bomberman_pos,enemie[0]["pos"])
    for i in enemie:
        distance = distance_to_object(bomberman_pos, i["pos"])
        if distance <= min_distance:
            min_distance = distance
            min_i = i
    return min_i

def distance_to_object(obj_1, obj_2):
    distance = math.sqrt(((obj_1[0] - obj_2[0]) ** 2) + ((obj_1[1] - obj_2[1]) ** 2))
    return distance

def real_map(map, wall_list):
    for row in map:
        for index, item in enumerate(row):
            if item == 2:
                row[index] = 0

    for w in wall_list:
        map[w[0]][w[1]] = 2
    return map

def get_nearest_spot(bomberman_pos, maze, ls):
    for spot in ls:
        if spot[0] >= 0 and spot[0] <= len(maze) - 2 and spot[1] >= 0 and spot[1] <= len(maze[0]) - 2 and maze[spot[0]][spot[1]] == 0:
            if astar(maze, bomberman_pos, spot) != None:
                return spot

def learn_path(path, ls=[]):
    ponto_x=[]
    ponto_y=[]
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


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
