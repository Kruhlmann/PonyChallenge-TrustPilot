import os
import subprocess
import numbers
import time

iter_path = os.path.join(os.environ["HOMEPATH"], "Desktop\\Mazes")
mazes = []

def is_number(value):
	return isinstance(value, numbers.Number)

def get_int_or_float(v):
	try:
		number_as_float = float(v)
		number_as_int = int(number_as_float)
		return number_as_int if number_as_float == number_as_int else number_as_float
	except ValueError:
		return 0

def get_mazes():
	global mazes
	mazes = []
	folders = os.walk(iter_path)
	for folder in folders:
		if folder[0].endswith("mazes"):
			mazes.append(folder[0].replace(iter_path, "").replace("\\mazes", ""))

def clear():
	if os.name in ('nt','dos'):
		subprocess.call("cls", shell=True)
	elif os.name in ('linux','osx','posix'):
		subprocess.call("clear", shell=True)
	else:
		print("\n"*120)

def print_menu():
	global mazes
	get_mazes()
	print(30*"=" + " Select a maze " + 30*"=")
	for i in range(0, len(mazes)):
		print(str(i) + "\t" + mazes[i]) 
	print(75*"=")

def show_maze_progression(maze_id):
	maze_folder = iter_path + maze_id + "\\mazes\\"
	i = 0
	while os.path.isfile(maze_folder + str(i) + ".txt"):
		clear()
		with open(maze_folder + str(i) + ".txt") as f: print(f.read())
		time.sleep(0.2)
		i += 1


if __name__ == "__main__":
	clear()
	print_menu()
	choice = get_int_or_float(input(">> "))

	while(choice < 0 or choice > len(mazes) - 1):
		print("Invalid choice")
		choice = get_int_or_float(input(">> "))

	show_maze_progression(mazes[choice])
