"""Evox.

Usage:
  evox get <package>...
  evox remove <package>...
  evox upgrade
  evox sync
  evox init
  evox (-h | --help)
  evox (-v | --version)

Options:
  get           Download and install a package
  remove        Remove a package (and optionnally its dependencies)
  sync          Sync the repos
  upgrade       Upgrade the system
  init          Initialize the default structure following the configuration
  -h --help     Show this screen.
  -v --version     Show version.

"""

import shutil
from docopt import docopt

import os, requests

import lib.instpkg as instpkg
import lib.log as log
import lib.config as config
import lib.rmpkg as rmpkg
import lib.db as db

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Evox 1.0.0')
    # We get the ROOT environment variable
    root = os.environ["ROOT"]
    if root == "":
        # If it's empty, we set it to /
        root = "/"
        
    if arguments['get']:
        for package in arguments['<package>']:
            instpkg.install_pkg(package)
            
    elif arguments['init']:
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
    
    elif arguments['remove']:
        for package in arguments['<package>']:
            # First, we check if the package is installed
            # We can use the lib.instpkg.is_installed function
            if instpkg.is_package_installed(package):
                # If it is, we remove it
                rmpkg.rmpkg(package)
                if not instpkg.is_package_installed(package):
                    # If it is removed, we log a success message
                    log.log_success("The package " + package + " has been removed.")
            else:
                # If it isn't, we log an error
                log.log_error("The package " + package + " is not installed.")

    elif arguments['sync']:
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

            # We simply get the INDEX file from the repository with requests
            # We can use the requests.get function
            index = requests.get(url + "/INDEX")

            # We open the INDEX file in the repository
            index_file = open(path + "/INDEX", "w")
            # We write the content of the INDEX file from the repository
            index_file.write(index.text)
            # We close the file
            index_file.close()

            # We can log a success message
            log.log_success("The repository " + repo + " has been synced.")

    elif arguments['upgrade']:
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
                # If the version of the package in the repository is higher than the installed version
                if repo_version != version:
                    # Log an info message
                    log.log_info("The package " + package + " is being upgraded from version " + version + " to version " + repo_version + ".")
                    # We remove the package
                    rmpkg.rmpkg(package, with_deps=False)
                    # We install the package
                    instpkg.install_pkg(package, is_dep=True, check_deps=False)
                    # We log a success message
                    log.log_success("The package " + package + " has been upgraded from version " + version + " to version " + repo_version + ".")