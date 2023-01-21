# DB Functions: read, register, unregister, update, delete, search, list
#
# The local DB File (/var/evox/packages/DB) is a text file with the following format:
# <package name> <version> <date>

import os

from lib.root import *

DB = root + "/var/evox/packages/DB"
def read_local():
    # Read the local DB file
    # Returns a list of tuples (name, version, date)
    # If the DB file doesn't exist, it returns an empty list
    db = []
    if os.path.isfile(DB):
        with open(DB, "r") as f:
            for line in f.readlines():
                db.append(tuple(line.split()))
    return db

def register_local(name: str, version: str, date: str):
    # Register a package in the local DB file

    with open(DB, "a") as f:
        f.write(name + " " + version + " " + date + "\n")

def unregister_local(name: str):
    # Unregister a package from the local DB file

    db = read_local()
    with open(DB, "w") as f:
        for pkg in db:
            if pkg[0] != name:
                f.write(pkg[0] + " " + pkg[1] + " " + pkg[2] + "\n")

def update_local(name: str, version: str, date: str):
    # Update a package in the local DB file

    db = read_local()
    with open(DB, "w") as f:
        for pkg in db:
            if pkg[0] != name:
                f.write(pkg[0] + " " + pkg[1] + " " + pkg[2] + "\n")
            else:
                f.write(name + " " + version + " " + date + "\n")

def read_remote(repo: str):
    # Read the remote DB file (/var/evox/repos/<repo>/DB)
    # The remote DB file has the following format:
    # <package name> <version>
    # Returns a list of tuples (name, version)
    # If the DB file doesn't exist, it returns an empty list
    db = []
    if os.path.isfile(root + "/var/evox/repos/" + repo + "/INDEX"):
        with open(root + "/var/evox/repos/" + repo + "/INDEX", "r") as f:
            for line in f.readlines():
                db.append(tuple(line.split()))
    return db

def get_installed_packages():
    # Returns a list of installed packages
    db = read_local()
    packages = {}
    for pkg in db:
        packages[pkg[0]] = pkg[1]
    return packages

def is_package_dependency(name: str, package: str = None):
    # Check if a package is a dependency of another package
    # Returns True if it is, False if it isn't
    db = read_local()
    for pkg in db:
        if package != None:
            if pkg[0] == package:
                continue
            if os.path.isfile(root + "/var/evox/packages/" + pkg[0] + "/PKGDEPS"):
                with open(root + "/var/evox/packages/" + pkg[0] + "/PKGDEPS", "r") as f:
                    for line in f.readlines():
                        if line.strip() == name:
                            return True
    return False

def get_remote_package_version(name: str):
    # Get the version of a package in the remote DB file
    # Returns the version if the package is in the DB file
    # Returns None if the package isn't in the DB file
    # Loop through all the repositories
    for repo in os.listdir(root + "/var/evox/repos"):
        db = read_remote(repo)
        # Loop through all the packages in the repository
        for pkg in db:
            # Check if the package is the one we're looking for
            if pkg[0] == name:
                # If it is, return the version
                return pkg[1]