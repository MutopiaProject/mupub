"""Command line interface (CLI) module.
"""

import argparse
import pkg_resources
import sys
import mupub


def _registered_commands(group='mupub.registered_commands'):
    """ Get our registered commands.

    Iterates the entry points and returns the registered commands as a
    dictionary.

    :param str group: The group in setup.py to iterate.
    :returns: A dict containing command-name:command pairs.

    """

    registered_commands = pkg_resources.iter_entry_points(group=group)
    return dict((c.name, c) for c in registered_commands)
        

def dispatch(argv):
    """
    """
    registered_commands = _registered_commands()
    parser = argparse.ArgumentParser(prog='mupub')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s version {0}'.format(mupub.__version__)
    )
    parser.add_argument(
        'command',
        choices=registered_commands.keys(),
    )
    parser.add_argument(
        'args',
        help=argparse.SUPPRESS,
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args(argv)

    main = registered_commands[args.command].load()

    main(args.args)
