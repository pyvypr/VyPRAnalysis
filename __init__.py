"""
VyPR analysis library.
Authors:
Marta Han - University of Zagreb, CERN
Joshua Dawes - University of Manchester, CERN.
"""
import sys

sys.path.append("VyPR/")

import json
import requests
import urllib2
from datetime import datetime
import pickle
from graphviz import Digraph
from pprint import pprint
import sys
import ast


server_url=json.load(open('config.json'))["verdict_server_url"]
def set_server(given_url):
    """
    server_url is a global variable which can be changed
    by passing a string to the set_server() function
    """
    global server_url
    server_url=given_url


"""
Import all functions from various modules.
"""

from utils import *
from orm import *