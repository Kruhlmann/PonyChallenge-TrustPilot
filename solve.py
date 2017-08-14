import urllib.request
import random
import os
import json

base_path = os.path.join(os.environ["HOMEPATH"], "Desktop\\Mazes")



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
		"maze-width": 15,
		"maze-height": 25,
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
		print(json_response)


if __name__ == "__main__":
	if(not os.path.isdir(base_path)):
		os.mkdir(base_path)

	maze = create_maze()
	if(maze["error"] == ""):
		maze_id = maze["response"]
		maze_payload = maze["payload"]
		download_maze_data(maze_id, maze_payload)
		for i in range(0, 100):
			move_player(random.choice(valid_directions), maze_id)
			open(base_path + "\\" + maze_id + "\\mazes\\{0}.txt".format(i), "w").write(get_maze_ascii(maze_id))

	else:
		print(maze["error"] + " upon creating maze: " + str(maze["exception"]))