from fabric.api import cd, run, sudo, env
from fabric.operations import put
import subprocess
import json
import socket
import time

with open('config.json', 'rb') as f:
    config = json.load(f)

env.hosts = config['host']
env.user = config['user']
env.password = config['password']


def upgrade():
    p = subprocess.Popen(["hg", "serve"])
    project_dir = "/home/{}/tunes".format(env.user)
    with cd(project_dir):
        run("hg pull -u")
        restart()
    p.kill()


def install():
    p = subprocess.Popen(["hg", "serve"])
    project_dir = "/home/{}".format(env.user)
    time.sleep(1)
    with cd(project_dir):
        run("hg clone http://{}:8000 tunes".format(socket.gethostbyname(socket.gethostname())))
    p.kill()

def install_init():
    put("tunes", "/etc/init.d/tunes", use_sudo=True, mode="755")
    sudo("chown root:root /etc/init.d/tunes")


def start():
    sudo("service tunes start", pty=False)


def stop():
    sudo("service tunes stop")

def restart():
    stop()
    start()
