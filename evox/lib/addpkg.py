# addpkg is a function that just install a package from a file.
#
# So, we can just call it with the path to the file.

import os
import shutil
import tarfile
import tempfile
import time

import lib.db as db
from lib.root import *

def addpkg(path: str, package: str, pkginfo: dict):        
    # The file is a simple tar.xz file, so we extract it
    # But in a temporary directory
    tmpdir = tempfile.mkdtemp(package)
    tar = tarfile.open(path)
    tar.extractall(tmpdir)
    tar.close()

    # We get the path to the package directory
    pkgdir = tmpdir + "/" + package
    
    # We copy all files from metadata/ to /var/evox/packages/<package>
    # We use shutil.copytree to copy the whole directory
    shutil.copytree(pkgdir + "/metadata", root + "/var/evox/packages/" + package)


    # We copy all files from data/ to /
    # We use shutil.copytree to copy the whole directory
    shutil.copytree(pkgdir + "/data", root + "/", dirs_exist_ok=True)

    # We copy all files from scripts/ to /var/evox/<package>/scripts
    # Note that the scripts/ directory is optional
    if os.path.isdir(pkgdir + "/scripts"):
        # We need to create the directory
        os.mkdir(root + "/var/evox/packages/" + package + "/scripts")
        shutil.copytree(pkgdir + "/scripts", root + "/var/evox/packages§" + package + "/scripts")

    # We remove the temporary directory
    shutil.rmtree(tmpdir)

    # We must add the package to the DB
    # But first, we need to get the current time (formatted like this: 2020-01-01_00:00:00)
    # We can use the time.strftime function
    date = time.strftime("%Y-%m-%d_%H:%M:%S")
    db.register_local(package, pkginfo['version'], date)
