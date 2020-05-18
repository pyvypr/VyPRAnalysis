import json
import sys

from VyPRAnalysis.http_requests import VerdictServerConnection

config_dict = None
server_url = None
connection = None
vypr_path = "VyPRAnalysis"
monitored_service_path = None

sys.path.append(vypr_path)


def set_config_file(config_file_name='config.json'):
    """
    Given config_file_name, read the configuration.
    """
    global config_dict, server_url, monitored_service_path, vypr_path
    config_dict = json.loads(open(config_file_name).read())
    server_url = config_dict["verdict_server_url"]
    monitored_service_path = config_dict["monitored_service"]
    vypr_path = config_dict["vypr_path"]

    set_server(server_url)
    set_vypr_path(vypr_path)


def set_server(given_url):
    """
    Set the server for the analysis library to ``given_url`` and then perform a handshake.
    """
    global server_url, connection
    server_url = given_url
    # try to connect
    connection = VerdictServerConnection(server_url)
    try:
        response = connection.handshake()
    except:
        print("Failed to connect to server.")


def get_server():
    global server_url
    return server_url


def get_connection(handshake=False):
    global connection
    if get_server() is None:
        raise Exception("No verdict server set.")
    if handshake:
        # try the handshake - most of the time this will just be done
        # when the server is set initially during configuration
        response = connection.handshake()
    return connection


def set_vypr_path(path):
    global vypr_path
    vypr_path = path
    sys.path.append(vypr_path)


def set_monitored_service_path(path):
    """
    Set the path of the monitored service to ``path`` .  No existence or permission checks are currently performed.
    """
    global monitored_service_path
    monitored_service_path = path
    return monitored_service_path


def get_monitored_service_path():
    global monitored_service_path
    return monitored_service_path


def prepare(db=None):
    """
    Given the database file name ``db``, set up an instance of a verdict server attached to that database
    in the background and then attempt to perform a handshake until the server is reachable.
    """
    import subprocess
    cmd = "cd VyPRServer/ && python run_service.py --port 9002 "
    if db:
        cmd = cmd + "--db %s &" % db
    else:
        cmd = cmd + "&"
    p = subprocess.Popen(cmd, shell=True)

    handshake_failed = True
    while handshake_failed:
        try:
            set_server("http://localhost:9002/")
            handshake_failed = False
        except:
            handshake_failed = True
    if not handshake_failed: print("Connected to server")


def teardown():
    """
    Shut down the verdict server to which the analysis library is currently pointing.

    Intended use is at the end of a script that began with ``prepare('...')``.
    """
    global connection
    try:
        connection.request("shutdown/")
    except:
        print("  ")


"""
Import all functions from various modules.
"""

from utils import *
from orm import *
