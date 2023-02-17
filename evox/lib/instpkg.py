import os
from lib.addpkg import addpkg
import lib.db as db
import lib.log as log
import lib.readevx as readevx
import lib.net as net
import lib.config as config

from urllib.parse import urlparse
from lib.root import *

def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False

def is_package_installed(package: str):
    # We get the list of installed packages
    installed_packages = db.get_installed_packages()

    # We check if the package is in the list
    if package in installed_packages:
        # If it is, we return True
        return True
    else:
        # If it isn't, we return False
        return False

def install_pkg(package: str, is_dep: bool = False, auto_accept: bool = False, check_deps: bool = True, upgrade: bool = False):
    current_dir = os.getcwd()
    path = package
    package_type = ""
    
    if not is_dep and os.path.exists(package):
        package_type = "file"
    elif is_url(package):
        package_type = "url"
    else:
        package_type = "name"

    if package_type == "file":
        package = package.split("/")[-1].split("-")
        package.pop()
        package = "-".join(package)

        if is_package_installed(package) and not upgrade:
            if is_dep or auto_accept:
                return
            elif log_installed():
                # We reinstall the package just like it was an upgrade
                install_file(path, check_deps=check_deps, upgrade=True)
            else:
                return
        else:
            install_file(path, check_deps=check_deps)

    elif package_type == "url":
        package = package.split("/")[-1].replace(".evx", "")
        if is_package_installed(package) and not upgrade:
            if is_dep or auto_accept:
                return
            elif log_installed():
                net.download(path, "/tmp/" + package.split("/")[-1])
                install_file("/tmp/" + package.split("/")[-1], check_deps=check_deps, upgrade=True)
            else:
                return
        else:
            net.download(path, "/tmp/" + package.split("/")[-1])
            install_file("/tmp/" + package.split("/")[-1], check_deps=check_deps)

    elif package_type == "name":
        if is_package_installed(package) and not upgrade:
            if is_dep or auto_accept:
                return
            elif log_installed():
                install_pkg(package, check_deps=check_deps, upgrade=True)
            else:
                return
        else:
            # We get the config
            repos = config.get_config()

            for repo in repos:
                # We get the URL of the repository
                url = repos[repo]["url"]
                # The path of the repository is /var/evox/repos/repo
                path = os.path.join(root, "var/evox/repos/" + repo)
                # If the repository doesn't exist, we create it
                # We can use the os.path.exists function
                if not os.path.exists(path):
                    # Log an error
                    log.log_error("Repository " + repo + " doesn't exist! (Maybe you have not synced it)")
                    exit(1)

            package_found = False
                            
            # We loop through the repositories
            for repo in repos:
                # We get the URL of the repository
                url = repos[repo]["url"]
                # The path of the repository is /var/evox/repos/repo
                path = os.path.join(root, "var/evox/repos/" + repo)

                # We get the index of the repository
                index = open(path + "/INDEX", "r")

                # We get the list of packages in the repository
                packages = index.read().splitlines()

                # We loop through the packages
                for pkg in packages:
                    # We get the name of the package
                    pkg_name = pkg.split(" ")[0]

                    # We check if the package is the one we want
                    if pkg_name == package:
                        # If it is, we get the version of the package
                        pkg_version = pkg.split(" ")[1]

                        # We get the path of the package
                        pkg_path = path + "/" + pkg_name + "-" + pkg_version + ".evx"

                        # We download the package
                        net.download(url + "/" + pkg_name + "-" + pkg_version + ".evx", pkg_path, True)

                        # We install the package
                        install_file(pkg_path, is_dep, auto_accept=auto_accept, check_deps=check_deps, upgrade=upgrade)

                        # We remove the package
                        os.remove(pkg_path)

                        # We set the package_found variable to True
                        package_found = True

                        # We break the loop
                        break

                if package_found:
                    break

            # If the package is not found, we log an error
            if not package_found:
                log.log_error("Package " + package + " not found in repositories!")
                exit(1)

    # To end, we display a message
    if not is_dep and is_package_installed(package) and not upgrade:
        log.log_success("Package installed successfully!")

    os.chdir(current_dir)

def install_file(package: str, is_dep: bool = False, auto_accept: bool = False, check_deps: bool = True, upgrade: bool = False):
    path = package

    if not is_dep:
        log.log_info("Installing package from file " + package.split("/")[-1] + "...")
        print()
    
    splitted_package = package.split("-")
    splitted_package.pop()
    package = "-".join(splitted_package).split("/")[-1]

    # We read the eVox file
    pkginfo = readevx.readevx(path, package)

    if not is_dep and not upgrade:
        # We display the needed informations
        log.log_info("Package name: " + pkginfo["name"])
        log.log_info("Package version: " + pkginfo["version"])
        log.log_info("Package description: " + pkginfo["description"])
    
        # And the optional ones
        if "url" in pkginfo:
            log.log_info("Package url: " + pkginfo["url"])
        if "license" in pkginfo:
            log.log_info("Package license: " + pkginfo["license"])

        # We add a blank line
        print()

    # We ask the user if he wants to install the package
    if is_dep or auto_accept or log.log_ask("Do you want to install this package?"):
        # For each dependency, we check if it's installed
        if "depends" in pkginfo and check_deps:
            # Log an info message
            installed_deps = []
            log.log_info("Checking dependencies...")
            for dep in pkginfo["depends"]:
                # If it's not installed, we install it
                if not is_package_installed(dep):
                    # Log an info message
                    log.log_info("Installing dependency " + dep + "...")
                    install_pkg(dep, is_dep=True)
                    # Log a success message
                    log.log_success("Dependency " + dep + " installed successfully!")
                    installed_deps.append(dep)

            print()
            
            # Log an info message
            if len(installed_deps) > 0:
                log.log_info("Dependencies installed successfully!")
                print()
            log.log_info("Installing package " + pkginfo["name"] + "...")
                
        # We just call the addpkg function
        addpkg(os.path.abspath(path), pkginfo["name"], pkginfo)

def log_installed():
    log.log_error("This package is already installed.")
    # Ask the user if he wants to reinstall the package
    if log.log_ask("Do you want to reinstall it?"):
        return True
    else:
        return False
