import urllib.request
import random
import os
import json
import math
import operator
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
		print(str(payload))
		payload_json = json.dumps(payload).encode("utf-8")
		req = urllib.request.Request(api_calls["get_maze"].format(maze_id), data=payload_json, headers={'Content-Type': 'application/json'})
		response = urllib.request.urlopen(req)
		json_response = json.loads(response.read().decode("utf-8"))
		return(json_response)


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

	path = []
	closed = []
	i = 0
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

	while player_x != end_point_x and player_y != end_point_y and res["state-result"] != "You lost. Killed by monster":
		maze = get_maze_state(maze_id)
		catalog = get_maze_catalog(maze)
		player_x = int((maze["pony"][0]) % maze_width)
		player_y = int(int(maze["pony"][0] - player_x) / maze_width)
		snooper_x = player_x
		snooper_y = player_y
		domokun_x = int(maze["domokun"][0]) % maze_width
		domokun_y = int(int(maze["domokun"][0] - domokun_x) / maze_width)
		end_point_x = int(maze["end-point"][0]) % maze_width
		end_point_y = int(int(maze["end-point"][0] - end_point_x) / maze_width)
		current_options = maze["data"][player_x + player_y * maze_width]
		options_right = maze["data"][(player_x + 1) + player_y * maze_width] if player_x < maze_width else []
		options_bottom = maze["data"][player_x + (player_y + 1) * maze_width] if player_y < maze_height else []

		closed.append(player_x + player_y * maze_width)

		avaliable_directions = {
			"north": "north" not in current_options,
			"east": "west" not in options_right,
			"south": "north" not in options_bottom,
			"west": "west" not in current_options,
		}

		avaliable_directions = []
		if("north" not in current_options):
			avaliable_directions.append("north")
		if("west" not in current_options):
			avaliable_directions.append("west")
		if("north" not in options_bottom): 
			avaliable_directions.append("south")
		if("west" not in options_right): 
			avaliable_directions.append("east")

		print(get_maze_ascii(maze_id))

		print("Current options: " + str(avaliable_directions))
		
		this_node_dist = catalog[(snooper_x + 0) + (snooper_y + 0) * maze_width]
		top_node_dist = 9999 if "north" in current_options else catalog[(snooper_x + 0) + (snooper_y - 1) * maze_width]
		bottom_node_dist = 9999 if "north" in options_bottom else catalog[(snooper_x + 0) + (snooper_y + 1) * maze_width]
		left_node_dist = 9999 if "west" in current_options else catalog[(snooper_x - 1) + (snooper_y + 0) * maze_width]
		right_node_dist = 9999 if "west" in options_right else catalog[(snooper_x + 1) + (snooper_y + 0) * maze_width]

		directions = {
			"north": 9998 if ((snooper_x + 0) + (snooper_y - 1) * maze_width) in closed else top_node_dist,
			"south": 9998 if ((snooper_x + 0) + (snooper_y + 1) * maze_width) in closed else bottom_node_dist,
			"west": 9998 if ((snooper_x - 1) + (snooper_y + 0) * maze_width) in closed else left_node_dist,
			"east": 9998 if ((snooper_x + 1) + (snooper_y + 0) * maze_width) in closed else right_node_dist
		}
		direction = sorted(directions.items(), key=operator.itemgetter(1))[0][0]
		print(directions)
		print("Moved " + direction)
		res = move_player(direction, maze_id)
		open(base_path + "\\" + maze_id + "\\mazes\\{0}.txt".format(i), "w").write(get_maze_ascii(maze_id))
		i += 1

if __name__ == "__main__":
	if(not os.path.isdir(base_path)):
		os.mkdir(base_path)

	maze = create_maze()
	if(maze["error"] == ""):
		maze_id = maze["response"]
		print("Created maze with data " + maze_id)
		maze_payload = maze["payload"]
		download_maze_data(maze_id, maze_payload)
		find_path_to_exit(maze_id)
		print(get_maze_ascii(maze_id))

		#for i in range(0, 100):
		#	move_player(random.choice(valid_directions), maze_id)
		#	open(base_path + "\\" + maze_id + "\\mazes\\{0}.txt".format(i), "w").write(get_maze_ascii(maze_id))

	else:
		print(maze["error"] + " upon creating maze: " + str(maze["exception"]))