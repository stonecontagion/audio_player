import youtube
from bottle import post, route, run, static_file, request
import json
import os
import psutil
import subprocess
import logging
import sys
logging.basicConfig(filename='tunes.log',level=logging.DEBUG)

is_windows = os.name == "nt"
EXAMPLE_URL = "https://www.youtube.com/watch?v=MlZ-yteWTxA"
BASE_URL = "https://www.youtube.com/watch?v={}"
if is_windows:
    PLAYER_CMD = r'youtube-dl -f 171 {} -o - | E:\\ffmpeg\\bin\\ffplay.exe -'
    BINARY_NAME = "ffplay.exe"
else:
    PLAYER_CMD = "youtube-dl -f 171 {} -o - > ./tunes.pipe | omxplayer ./tunes.pipe"
    BINARY_NAME = "omxplayer.bin"
currently_playing = None


def system_command(cmd):
    logging.info("system command '%s'", cmd)
    logging.info("cmd returned: %s", subprocess.check_output(cmd, shell=True))

def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)


def ensure_fifo():
    if is_windows:
        return
    if os.path.exists('./tunes.pipe'):
        system_command('unlink ./tunes.pipe')
    system_command('mkfifo ./tunes.pipe')


@post('/search/<query>')
def search(query):
    logging.info("got search request for %s", query)
    return json.dumps(youtube.youtube_search(query, 10))
 
@post('/play')
def play():
    global currently_playing
    stop()
    ensure_fifo()
    data = request.json
    name = data['name']
    track = data['track_id']
    logging.info("request to play %s %s", track, name)
    url = BASE_URL.format(track)
    process_command = PLAYER_CMD.format(url)
    logging.info("process command: %s", process_command)
    process = subprocess.Popen(
        process_command,
        shell=True
    )
    currently_playing = process
    currently_playing.data = data
    return json.dumps({})

def playing_started():
    for p in psutil.process_iter():
        try:
            if p.name() == BINARY_NAME:
                return True
        except psutil.Error:
            pass
    return False

@route('/playing')
@post('/playing')
def playing():
    global currently_playing
    if currently_playing:
        data = currently_playing.data
        data['started'] = playing_started()
        return json.dumps(currently_playing.data)
    else:
        return json.dumps({})

@post('/stop')
def stop():
    global currently_playing
    if currently_playing and currently_playing.poll() is None:
        if not is_windows:
            system_command("sudo kill -9 `pidof omxplayer.bin`")
        else:
            try:
                kill_proc_tree(currently_playing.pid)
            except psutil.NoSuchProcess:
                pass
    currently_playing = None

@route('/power')
@post('/power')
def restart():
    subprocess.Popen("sudo halt".split())

@route('/static/<path:path>')
def static(path):
    return static_file(path, root="./static")

@route('/')
def index():
    return static_file("index.html", root="./static")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if not is_windows:
    fpid = os.fork()
    if fpid!=0:
        # Running as daemon now. PID is fpid
        sys.exit(0)
    system_command("echo {} > /var/run/tunes.pid".format(os.getpid()))
run(host='0.0.0.0', port=8080, debug=True)
