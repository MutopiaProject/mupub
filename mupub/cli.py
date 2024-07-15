"""Command line interface (CLI) module.
"""

import argparse
import logging
from logging.handlers import RotatingFileHandler
import os
import pkg_resources
import sys
import textwrap
import mupub

_FILEFMT = "%(asctime)s %(levelname)s %(name)s %(message)s"
_CONSOLEFMT = "%(levelname)-8s %(name)-12s %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"

_LONG_DESCRIPTION = """
This is a command-line utility for managing the publication of
Mutopia Project contributions. All functionality is provided by
commands within this utility:

    init  - Initialize local data, syncbronize id's with mutopia site.
    check - Reviews the contributed piece for validity.
    tag   - Modifies the header with MutopiaProject fields.
    build - Builds a complete set of output files for publication.
    clean - Clears all build products.
"""


def _configure_logging(verbose):
    if "logging" not in mupub.CONFIG_DICT.sections():
        return
    logdict = mupub.CONFIG_DICT["logging"]

    # Set the module logger to the lowest reasonable level (DEBUG)
    mupub_logger = logging.getLogger("mupub")
    mupub_logger.setLevel(logging.DEBUG)

    if logdict.getboolean("log_to_file", True):
        # Add a rotating logfile handler
        logpath = os.path.join(
            mupub.CONFIG_DIR, logdict.get("logfilename", "mupub-errors.log")
        )
        file_handler = RotatingFileHandler(logpath, maxBytes=1024 * 100, backupCount=3)
        # Logging is always INFO level
        file_handler.setLevel(logging.INFO)
        logform = logging.Formatter(fmt=_FILEFMT, datefmt=_DATEFMT)
        file_handler.setFormatter(logform)
        mupub_logger.addHandler(file_handler)

    # If verbose the console logging handler is set to DEBUG,
    # otherwise it gets the configured level.
    if verbose:
        n_level = logging.DEBUG
    else:
        # Check configuration for an alternate level.
        level = logdict.get("loglevel", "INFO")
        n_level = getattr(logging, level.upper(), None)
        # Default to DEBUG in the event of a misspelled level
        if not isinstance(n_level, int):
            n_level = logging.DEBUG
            mupub_logger.warning("%s is an invalid level. Check config." % level)

    console = logging.StreamHandler()
    console.setLevel(n_level)
    console_form = logging.Formatter(fmt=_CONSOLEFMT, datefmt=_DATEFMT)
    console.setFormatter(console_form)
    mupub_logger.addHandler(console)


def _registered_commands(group="mupub.registered_commands"):
    """Get our registered commands.

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
        prog="mupub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(_LONG_DESCRIPTION),
        epilog="Use mupub <command> --help for specific command help",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s version {0}".format(mupub.__version__),
    )
    parser.add_argument("--verbose", action="store_true", help="louder")
    parser.add_argument(
        "command",
        choices=registered_commands.keys(),
    )

    parser.add_argument(
        "args",
        help=argparse.SUPPRESS,
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args(argv)

    _configure_logging(args.verbose)

    main = registered_commands[args.command].load()

    main(args.args)
