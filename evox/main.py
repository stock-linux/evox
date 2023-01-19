"""Evox.

Usage:
  evox get <package>...
  evox remove <package>...
  evox sync
  evox init
  evox (-h | --help)
  evox (-v | --version)

Options:
  get           Download and install a package
  remove        Remove a package (and optionnally its dependencies)
  sync          Sync the repos
  init          Initialize the default structure following the configuration
  -h --help     Show this screen.
  -v --version     Show version.

"""

from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Evox 1.0.0')
    print(arguments)