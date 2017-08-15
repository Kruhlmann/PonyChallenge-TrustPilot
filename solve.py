import urllib.request
import random
import os
import json
import math
import operator
import subprocess
import time
import sys
from PIL import Image

base_path = os.path.join(os.environ["HOMEPATH"], "Desktop\\Mazes")

maze_width = 15
maze_height = 25

cells = []
cell_clusters = []

valid_directions = [
	"north",
	"south",
	"east",
	"west"
]

pony_names = [
	"Fluttershy",
	"Twilight Sparkle",
	"Applejack",
	"Rainbow Dash",
	"Pinkie Pie",
	"Rarity",
	"Spike"
]

api_calls = {
	"create_maze": "https://ponychallenge.trustpilot.com/pony-challenge/maze",
	"get_maze": "https://ponychallenge.trustpilot.com/pony-challenge/maze/{0}",
	"print_maze": "https://ponychallenge.trustpilot.com/pony-challenge/maze/{0}/print"
}

def create_maze():
	payload = {
		"maze-width": maze_width,
		"maze-height": maze_height,
		"maze-player-name": random.choice(pony_names)
	}
	payload_json = json.dumps(payload).encode("utf-8")
	try:
		req = urllib.request.Request(api_calls["create_maze"], data=payload_json, headers={'Content-Type': 'application/json'})
		response = urllib.request.urlopen(req)
		json_response = json.loads(response.read().decode("utf-8"))
		return {
			"response": json_response["maze_id"],
			"payload": payload,
			"error": ""
		}
	except ValueError as e:
		return {"error": "ValueError", "exception": e}
	except urllib.error.URLError as e:
		return {"error": "URLError", "exception": e}

def download_maze_data(maze_id, payload):
	if(os.path.isdir(base_path + "\\" + maze_id)):
		print("Error: Maze with ID " + maze_id + " has already been processed")
		exit()
	else:
		os.mkdir(base_path + "\\" + maze_id)
		os.mkdir(base_path + "\\" + maze_id + "\\mazes")

	header_file = open(base_path + "\\" + maze_id + "\\header.txt", "w")
	initial_maze = open(base_path + "\\" + maze_id + "\\mazes\\start.txt", "w")
	header_file.write("Maze ID: " + maze_id + "\n" + str(payload))
	initial_maze.write(get_maze_ascii(maze_id))

def get_maze_state(maze_id):
	req = urllib.request.Request(api_calls["get_maze"].format(maze_id))
	response = urllib.request.urlopen(req)
	return json.loads(response.read().decode("utf-8"))

def get_maze_ascii(maze_id):
	req = urllib.request.Request(api_calls["print_maze"].format(maze_id))
	response = urllib.request.urlopen(req)
	return response.read().decode("utf-8")

def move_player(direction, maze_id):
	if(direction not in valid_directions):
		print("Invalid direction: " + direction)
	else:
		payload = {
			"direction": direction
		}
		payload_json = json.dumps(payload).encode("utf-8")
		req = urllib.request.Request(api_calls["get_maze"].format(maze_id), data=payload_json, headers={'Content-Type': 'application/json'})
		response = urllib.request.urlopen(req)
		json_response = json.loads(response.read().decode("utf-8"))
		return(json_response)

def clear():
	if os.name in ('nt','dos'):
		subprocess.call("cls", shell=True)
	elif os.name in ('linux','osx','posix'):
		subprocess.call("clear", shell=True)
	else:
		print("\n"*120)

def find_path_to_exit(maze_id):

	def get_maze_catalog(maze):
		catalog = []
		for y in range(0, maze_height):
			for x in range(0, maze_width):
				end_point_x = int(maze["end-point"][0]) % maze_width
				end_point_y = int(int(maze["end-point"][0] - end_point_x) / maze_width)
				catalog.append(math.sqrt((x - end_point_x)**2 + (y - end_point_y)**2))
		return catalog

	def print_catalog(catalog):
		with open(base_path + "\\" + maze_id + "\\catalog.txt", "w") as f:
			for y in range(0, maze_height):
				f.write("Line #" + str(y) + ":\t")
				for x in range(0, maze_width):
					f.write(str(int(catalog[x + y * maze_width])) + "\t")
				f.write("\n")
	
	res = {
		"state-result": "None"
	}

	player_x = 0
	player_y = 0
	domokun_x = 0
	domokun_y = 0
	end_point_x = maze_width
	end_point_y = maze_height
	snooper_x = 0
	snooper_y = 0
	maze = get_maze_state(maze_id)
	catalog = get_maze_catalog(maze)
	heat_map = [0] * (maze_width * maze_height)
	old_domokun_index = -1

	j = 0
	while player_x != end_point_x and player_y != end_point_y and res["state-result"] != "You lost. Killed by monster":
		for i in range(0, len(heat_map)):
			if heat_map[i] > 0:
				heat_map[i] -= 1
		maze = get_maze_state(maze_id)
		player_x = int((maze["pony"][0]) % maze_width)
		player_y = int(int(maze["pony"][0] - player_x) / maze_width)
		snooper_x = player_x
		snooper_y = player_y
		domokun_x = int(maze["domokun"][0]) % maze_width
		domokun_y = int(int(maze["domokun"][0] - domokun_x) / maze_width)
		end_point_x = int(maze["end-point"][0]) % maze_width
		end_point_y = int(int(maze["end-point"][0] - end_point_x) / maze_width)
		
		current_options = maze["data"][player_x + player_y * maze_width]
		
		if player_x >= maze_width:
			options_right = []
		else:
			options_right = maze["data"][(player_x + 1) + player_y * maze_width]

		if player_y >= maze_height:
			options_bottom = []
		else:
			options_bottom = maze["data"][player_x + (player_y + 1) * maze_width]
		
		top_index = (snooper_x + 0) + (snooper_y - 1) * maze_width
		bot_index = (snooper_x + 0) + (snooper_y + 1) * maze_width
		lef_index = (snooper_x - 1) + (snooper_y + 0) * maze_width
		rig_index = (snooper_x + 1) + (snooper_y + 0) * maze_width

		top_node_dist = 9998 if "north" in current_options or top_index < 0 else catalog[top_index]
		bot_node_dist = 9998 if "north" in options_bottom or bot_index > maze_height * maze_height else catalog[bot_index]
		lef_node_dist = 9998 if "west" in current_options or lef_index < 0 else catalog[lef_index]
		rig_node_dist = 9998 if "west" in options_right or rig_index > maze_width * maze_height else catalog[rig_index]

		heat_map[player_x + player_y * maze_width] = 100
		if old_domokun_index > -1:
			heat_map[old_domokun_index] -= 9998
		heat_map[domokun_x + domokun_y * maze_width] = 9999
		old_domokun_index = domokun_x + domokun_y * maze_width

		directions = {
			"north": top_node_dist + heat_map[(snooper_x + 0) + (snooper_y - 1) * maze_width],
			"south": bot_node_dist + heat_map[(snooper_x + 0) + (snooper_y + 1) * maze_width],
			"west": lef_node_dist + heat_map[(snooper_x - 1) + (snooper_y + 0) * maze_width],
			"east": rig_node_dist + heat_map[(snooper_x + 1) + (snooper_y + 0) * maze_width]
		}
		direction = sorted(directions.items(), key=operator.itemgetter(1))[0][0]
		res = move_player(direction, maze_id)
		open(base_path + "\\" + maze_id + "\\mazes\\{0}.txt".format(j), "w").write(get_maze_ascii(maze_id))
		print("Current distance: {0:.2f}".format(catalog[player_x + player_y * maze_width]))
		j += 1
	print("Result: " + res["state-result"])

if __name__ == "__main__":
	clear()
	if(not os.path.isdir(base_path)):
		os.mkdir(base_path)

	maze = create_maze()
	if(maze["error"] == ""):
		maze_id = maze["response"]
		print("Created maze with data " + maze_id)
		maze_payload = maze["payload"]
		download_maze_data(maze_id, maze_payload)
		find_path_to_exit(maze_id)

		#for i in range(0, 100):
		#	move_player(random.choice(valid_directions), maze_id)
		#	open(base_path + "\\" + maze_id + "\\mazes\\{0}.txt".format(i), "w").write(get_maze_ascii(maze_id))
	else:
		print(maze["error"] + " upon creating maze: " + str(maze["exception"]))