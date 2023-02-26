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

def get_remote_packages():
    # Returns a list of tuples (name, version) of all the packages in the remote DB files
    packages = []
    # Loop through all the repositories
    for repo in os.listdir(root + "/var/evox/repos"):
        db = read_remote(repo)
        # Loop through all the packages in the repository
        for pkg in db:
            # Check if the package is already in the list
            found = False
            for package in packages:
                if package[0] == pkg[0]:
                    found = True
                    break
            # If it isn't, add it to the list
            if not found:
                packages.append(pkg)
    return packages

def get_local_package_info(package: str):
    # Read /var/evox/packages/<package>/PKGINFO
    # Returns a dictionary with the package info
    info = {}
    if os.path.isfile(root + "/var/evox/packages/" + package + "/PKGINFO"):
        with open(root + "/var/evox/packages/" + package + "/PKGINFO", "r") as f:
            for line in f.readlines():
                info[line.split(" = ")[0]] = line.split(" = ")[1].strip()
    return info

def get_local_package_pkgrel(package: str):
    # Read /var/evox/packages/<package>/PKGREL
    # Returns the package release
    # The pkgrel is a field in the PKGINFO file
    # So we need to read the PKGINFO file to get the pkgrel
    pkgrel = None
    if os.path.isfile(root + "/var/evox/packages/" + package + "/PKGINFO"):
        with open(root + "/var/evox/packages/" + package + "/PKGINFO", "r") as f:
            for line in f.readlines():
                if line.split(" = ")[0] == "pkgrel":
                    pkgrel = int(line.split(" = ")[1].strip())

    return pkgrel

def get_remote_package_pkgrel(package: str):
    # We read the pkgrel of a remote package in the INDEX file
    # The INDEX file has the following format:
    # <package name> <version> <pkgrel>
    # So we need to read the INDEX file to get the pkgrel
    pkgrel = None
    # Loop through all the repositories
    for repo in os.listdir(root + "/var/evox/repos"):
        if os.path.isfile(root + "/var/evox/repos/" + repo + "/INDEX"):
            with open(root + "/var/evox/repos/" + repo + "/INDEX", "r") as f:
                for line in f.readlines():
                    if line.split()[0] == package:
                        pkgrel = int(line.split()[2])

    return pkgrel

def get_local_package_pkgdeps(package: str):
    # Read /var/evox/packages/<package>/PKGDEPS
    # Returns a list of dependencies
    deps = []
    if os.path.isfile(root + "/var/evox/packages/" + package + "/PKGDEPS"):
        with open(root + "/var/evox/packages/" + package + "/PKGDEPS", "r") as f:
            for line in f.readlines():
                deps.append(line.strip())
    return deps