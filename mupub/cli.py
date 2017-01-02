"""Command line interface (CLI) module.
"""

import argparse
import pkg_resources
import sys
import textwrap
import mupub

_LONG_DESCRIPTION="""
This is a command-line utility for managing the publication of
Mutopia Project contributions. All unctionality is provided by
commands within this utility:

    init  - Initialize workspace. Creates $HOME/.mupub
    check - Reviews the contributed piece for validity.
    tag   - Modifies the header with MutopiaProject fields.
    build - Builds a complete set of output files for publication.
    clean - Clears all build products.
"""

def _registered_commands(group='mupub.registered_commands'):
    """ Get our registered commands.

    Iterates the entry points and returns the registered commands as a
    dictionary.

    :param str group: The group in setup.py to iterate.
    :return: A table containing command-name:command pairs.
    :rtype: dict
    """

    registered_commands = pkg_resources.iter_entry_points(group=group)
    return dict((c.name, c) for c in registered_commands)


def dispatch(argv):
    """Dispatch to command with arguments.

    The main entry point calls this routine to dispatch to one of the
    various commands. Once the command is deciphered from the
    registered commands in ``setup.py``, control passes to that
    command with the remainder of the arguments.

    """
    registered_commands = _registered_commands()
    parser = argparse.ArgumentParser(
        prog='mupub',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(_LONG_DESCRIPTION),
        epilog='Use mupub <command> --help for specific command help',
)
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
