# addpkg is a function that just install a package from a file.
#
# So, we can just call it with the path to the file.

import os
import shutil
import time
import tempfile
import tarfile
import zstandard

import lib.db as db
from lib.root import *

def copy_dir(src: str, dest: str):
    # Get all files and subfiles in the directory
    files = os.listdir(src)
    links = []

    # For each file, we copy it to the destination
    for file in files:
        # If the file is a link, we add it to the links list
        if os.path.islink(os.path.join(src, file)):
            links.append(file)
        elif os.path.isdir(os.path.join(src, file)):
            # If it's a directory, we copy it recursively
            copy_dir(os.path.join(src, file), os.path.join(dest, file))
        else:
            # If it's a file, we just move it
            os.makedirs(os.path.join(dest, os.path.dirname(file)), exist_ok=True)
            # If the file exists (in case of upgrade), we remove it
            if os.path.exists(os.path.join(dest, file)):
                os.remove(os.path.join(dest, file))
            
            # Get the file owners
            # We can use the os.stat function
            stat = os.stat(os.path.join(src, file))
            shutil.move(os.path.join(src, file), os.path.join(dest, file))
            # We set the file owners
            # We can use the os.chown function
            os.chown(os.path.join(dest, file), stat.st_uid, stat.st_gid)
            # We must also set the mode 
            # We can use the os.chmod function
            os.chmod(os.path.join(dest, file), stat.st_mode)

    # For each link, we create it
    for link in links:
        # We get the link target
        # We can use the os.readlink function
        target = os.readlink(os.path.join(src, link))
        # We create the link
        # We can use the os.symlink function
        # But first, just check if the link already exists
        if not os.path.exists(os.path.join(dest, link)):
            os.makedirs(os.path.join(dest, os.path.dirname(link)), exist_ok=True)
            try:
                os.symlink(target, os.path.join(dest, link))
            except:
                pass

    if len(files) == 0:
        # If the directory is empty, we create an empty directory at the destination
        os.makedirs(dest, exist_ok=True)

def addpkg(path: str, package: str, pkginfo: dict):
    tempdir = tempfile.mkdtemp(dir=root + '/tmp')
    os.chdir(tempdir)

    # The package is a tar zst archive
    # We must use zstandard to decompress it
    # We use a decompressor
    with open(path, "rb") as f:
        dctx = zstandard.ZstdDecompressor()
        reader = dctx.stream_reader(f)
        with open(package + ".tar", "wb") as out:
            shutil.copyfileobj(reader, out)
        
    # We can now extract the archive
    with tarfile.open(package + ".tar") as tar:
        tar.extractall()
    # We remove the archive
    os.remove(package + ".tar")

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

    shutil.rmtree(tempdir)
    os.chdir(root)
    
    # If ldconfig is installed, we run it
    # But we only run it when the root is / (not when we are in a chroot)
    if root == "/" and os.path.exists("/sbin/ldconfig"):
        os.system("/sbin/ldconfig")
    
    # if the package has a post-install script, we execute it
    # But only when the root is / (not when we are in a chroot)
    if os.path.exists(os.path.join(root, "var/evox/packages/", package, "scripts", "PKGPOST")) and root == "/":
        # But first, chdir to the root
        os.system("bash " + os.path.join(root, "var/evox/packages/", package, "scripts", "PKGPOST"))
