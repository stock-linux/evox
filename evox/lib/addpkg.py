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

def copy_dir(src: str, dest: str):
    # Get all files and subfiles in the directory
    files = os.listdir(src)

    # For each file, we copy it to the destination
    for file in files:
        if os.path.isdir(os.path.join(src, file)):
            # If it's a directory, we copy it recursively
            copy_dir(os.path.join(src, file), os.path.join(dest, file))
        else:
            # If it's a file, we just move it
            os.makedirs(os.path.join(dest, os.path.dirname(file)), exist_ok=True)
            shutil.move(os.path.join(src, file), os.path.join(dest, file))

def addpkg(path: str, package: str, pkginfo: dict):     
    tempdir = tempfile.mkdtemp()

    # The file is a simple tar.xz file, so we extract it
    tar = tarfile.open(path, dereference=True)
    tar.extractall(tempdir)
    tar.close()

    # We copy the content of data/ to the root
    copy_dir(os.path.join(tempdir, package, "data"), root)

    # We copy the content of metadata/ to the package directory
    copy_dir(os.path.join(tempdir, package, "metadata"), os.path.join(root, "var/evox/packages/", package))

    # And we copy the content of scripts/ to the package directory
    copy_dir(os.path.join(tempdir, package, "scripts"), os.path.join(root, "var/evox/packages/", package, "scripts"))

    # We must add the package to the DB
    # But first, we need to get the current time (formatted like this: 2020-01-01_00:00:00)
    # We can use the time.strftime function
    date = time.strftime("%Y-%m-%d_%H:%M:%S")
    db.register_local(package, pkginfo['version'], date)
