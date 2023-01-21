# config module reads the config file and returns a dictionary of the repositories
# and their URL

import os

import lib.log as log

from lib.root import *

def get_config():
    # We get the ROOT environment variable
    if not "ROOT" in os.environ:
        root = "/"
    else:
        root = os.environ["ROOT"]

    # We open the config file
    config_file = open(root + "/etc/evox.conf", "r")

    # We create a dictionary to store the repositories
    repos = {}

    # We read the config file line by line
    for line in config_file:
        # We split the line by spaces
        line = line.split(" ")

        # We check if the line is a comment
        if line[0][0] == "#":
            # If it is, we skip it
            continue

        # We check if the line is a repository
        if line[0] == "REPO":
            # If it is, we add it to the repos dictionary
            repos[line[1].strip()] = {"url": line[2].strip()}

    # We close the config file
    config_file.close()

    # We return the repos dictionary
    return repos