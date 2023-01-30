# rmpkg is the module that handles the removal of packages

import os
import shutil

from lib.root import *
import lib.log as log
import lib.db as db
import lib.instpkg as instpkg

def rmtree(pkgtree: list):
    # For each line in the PKGTREE file
    dirs_list = []
    for line in pkgtree:
        # We get the path to the file
        path = os.path.join(root, line)

        # If the file exists
        if os.path.exists(path):
            # We check if it's a directory
            if os.path.isdir(path):
                # If it is, we add it to the dirs_list
                dirs_list.append(path)
            else:
                # If it isn't, we remove it
                os.remove(path)

        # We reverse the dirs_list
    dirs_list.reverse()

    # We remove the directories only if they're empty
    for d in dirs_list:
        # If it is a link, check that it's not broken
        if os.path.islink(d):
            if not os.path.exists(os.path.join(os.path.dirname(d), os.readlink(d))):
                os.remove(d)
                continue
        # We check if the directory is empty
        if len(os.listdir(d)) == 0:
            # If it is a link, we remove it by using os.remove
            if os.path.islink(d):
                os.remove(d)
            else:
                # If not, we remove the path as a directory
                os.rmdir(d)


def rmpkg(package: str, with_deps: bool = True):
    system_pkgs = ["evox", "glibc"]

    if package in system_pkgs:
        log.log_error("You cannot remove the package " +
                      package + " because it's a system package.")
        return
    # We get the path to the package directory
    pkgdir = root + "/var/evox/packages/" + package

    # We check if the package has dependencies by reading the PKGDEPS file
    # Note: The PKGDEPS file is optional
    if with_deps and os.path.exists(pkgdir + "/PKGDEPS"):
        # If it exists, we read it
        with open(pkgdir + "/PKGDEPS", "r") as f:
            deps = f.read().splitlines()
            # For each dependency
            for dep in deps:
                # We check if the package is installed
                if instpkg.is_package_installed(dep):
                    # We check if the package is a dependency of another package
                    if not db.is_package_dependency(dep, package):
                        # Log an info message
                        log.log_info("Removing dependency " + dep)
                        # If it isn't, we remove it
                        rmpkg(dep)
                        # We log a success message
                        log.log_success("Removed dependency " + dep)
                        print()
                    else:
                        # Log an info message
                        log.log_info(
                            "Package " + dep + " is a dependency of another package, not removing it")

    # We get the PKGTREE file
    rmtree(open(pkgdir + "/PKGTREE", "r").read().splitlines())

    # We remove the package directory
    shutil.rmtree(pkgdir)

    # We remove the package from the DB
    db.unregister_local(package)
