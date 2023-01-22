"""Evox.

Usage:
  evox get <package>...
  evox remove <package>...
  evox upgrade
  evox info <package>
  evox search <expr>
  evox sync
  evox init
  evox (-h | --help)
  evox (-v | --version)

Options:
  get           Download and install a package
  remove        Remove a package (and optionnally its dependencies)
  search        Search a package
  info          Show information about an installed package
  sync          Sync the repos
  upgrade       Upgrade the system
  init          Initialize the default structure following the configuration
  -h --help     Show this screen.
  -v --version     Show version.

"""

import shutil
from docopt import docopt

import os

import lib.instpkg as instpkg
import lib.log as log
import lib.config as config
import lib.rmpkg as rmpkg
import lib.db as db
import lib.net as net

from lib.root import *

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Evox 1.0.0')

    if arguments['get']:
        for package in arguments['<package>']:
            instpkg.install_pkg(package)

    if arguments['init']:
        # We just need to create the /var/evox/packages directory, the /var/evox/repos directory
        # We can use the os.makedirs function
        os.makedirs(root + "/var/evox/packages", exist_ok=True)
        os.makedirs(root + "/var/evox/repos", exist_ok=True)
        os.makedirs(root + "/etc", exist_ok=True)
        # We also need to copy the /etc/evox.conf file
        shutil.copyfile("/etc/evox.conf", root + "/etc/evox.conf")
        # For each repository, we create a directory
        # When we get the config, we get a dictionary of the repositories
        # The dictionary is structured like this:
        # {"repo_name": {"path": "path", "url": "url"}}
        # We can use the config.get_config() function to get the dictionary
        for repo in config.get_config():
            os.makedirs(root + "/var/evox/repos/" + repo, exist_ok=True)

        # We also need to create the /var/evox/packages/DB file
        # We can use the open function
        open(root + "/var/evox/packages/DB", "w").close()

        # We can log a success message
        log.log_success("The default structure has been created.")

    if arguments['remove']:
        for package in arguments['<package>']:
            # First, we check if the package is installed
            # We can use the lib.instpkg.is_installed function
            if instpkg.is_package_installed(package):
                # If it is, we remove it
                rmpkg.rmpkg(package)
                if not instpkg.is_package_installed(package):
                    # If it is removed, we log a success message
                    log.log_success("The package " + package +
                                    " has been removed.")
            else:
                # If it isn't, we log an error
                log.log_error("The package " + package + " is not installed.")

    if arguments['sync']:
        # We get the config
        repos = config.get_config()

        # We loop through the repositories
        for repo in repos:
            # We get the URL of the repository
            url = repos[repo]["url"]
            # The path of the repository is /var/evox/repos/repo
            path = root + "/var/evox/repos/" + repo

            # If the repository doesn't exist, we create it
            # We can use the os.path.exists function
            if not os.path.exists(path):
                # We can use the os.makedirs function
                os.makedirs(path, exist_ok=True)

            # We simply get the INDEX file from the repository with net.download
            index = net.download(url + "/INDEX")

            # We open the INDEX file in the repository
            index_file = open(path + "/INDEX", "w")
            # We write the content of the INDEX file from the repository
            index_file.write(index.text)
            # We close the file
            index_file.close()

            # We can log a success message
            log.log_success("The repository " + repo + " has been synced.")

    if arguments['upgrade']:
        # We get the installed packages
        installed_packages = db.get_installed_packages()

        # We loop through the packages
        for package in installed_packages:
            # We check if the package is in the repository thanks to the os.path.exists function
            if os.path.exists(root + "/var/evox/packages/" + package):
                # If it is, we get the version of the package
                version = installed_packages[package]
                # We get the version of the package in the repository
                repo_version = db.get_remote_package_version(package)
                local_pkgrel = db.get_local_package_pkgrel(package)
                remote_pkgrel = db.get_remote_package_pkgrel(package)
                # If the version of the package in the repository is higher than the installed version
                if repo_version != version or local_pkgrel < remote_pkgrel:
                    # Log an info message
                    log.log_info("The package " + package + " is being upgraded from version " + version + "-" + str(
                        local_pkgrel) + " to version " + repo_version + "-" + str(remote_pkgrel) + ".")
                    # We remove the package
                    rmpkg.rmpkg(package, with_deps=False)
                    # We install the package
                    instpkg.install_pkg(package, is_dep=True, check_deps=False)
                    # We log a success message
                    log.log_success("The package " + package + " has been upgraded from version " + version + "-" + str(
                        local_pkgrel) + " to version " + repo_version + "-" + str(remote_pkgrel) + ".")

    if arguments['search']:
        # We get the config
        repos = config.get_config()
        # We get the expression
        expr = arguments['<expr>']
        # We create a list of packages
        packages = db.get_remote_packages()
        installed_packages = db.get_installed_packages()
        # We loop through the packages
        for package in packages:
            # If the package contains the expression
            if expr in package[0]:
                if instpkg.is_package_installed(package[0]):
                    local_pkgrel = db.get_local_package_pkgrel(package[0])
                    # We log the package
                    log.log_info(package[0] + " (" + package[1] + "-" + package[2] + ")[Installed " +
                                 installed_packages[package[0]] + "-" + str(local_pkgrel) + "]")
                else:
                    # We log the package
                    log.log_info(
                        package[0] + " (" + package[1] + "-" + package[2] + ")")

    if arguments['info']:
        # We get the config
        repos = config.get_config()
        # We get the package
        package = arguments['<package>'][0]
        # We get the package info
        info = db.get_local_package_info(package)
        # We log the info
        log.log_info("Name: " + info["name"])
        log.log_info("Version: " + info["version"])
        log.log_info("Description: " + info["description"])
        log.log_info("Source: " + info["source"])
        # Log optional info
        if "license" in info:
            log.log_info("License: " + info["license"])
        if "url" in info:
            log.log_info("URL: " + info["url"])
        if "maintainer" in info:
            log.log_info("Maintainer: " + info["maintainer"])
