import os
import datetime

log_path = os.path.join(os.environ["HOMEPATH"], "Desktop\\maze_log.txt")

def log(maze_id, msg):
	with open(log_path, "a") as f:
		f.write("[{0}] {1}: {2}\n".format(str(datetime.datetime.now()), maze_id, msg))