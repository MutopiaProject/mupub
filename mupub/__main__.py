"""The main console script entry point.

"""

import logging
import os.path
import sys
from mupub.cli import dispatch
import mupub
from logging.handlers import RotatingFileHandler

_FILEFMT = '%(asctime)s %(levelname)s %(name)s %(message)s'
_CONSOLEFMT = '%(levelname)-8s %(name)-12s %(message)s'
_DATEFMT = '%Y-%m-%d %H:%M:%S'


def _configure_logging():
    if 'logging' not in mupub.CONFIG_DICT.sections():
        return
    logdict = mupub.CONFIG_DICT['logging']

    # Set the module logger to the lowest reasonable level (DEBUG)
    mupub_logger = logging.getLogger('mupub')
    mupub_logger.setLevel(logging.DEBUG)

    # Check configuration for an alternate level.
    level = logdict.get('loglevel', 'INFO')
    n_level = getattr(logging, level.upper(), None)
    if not isinstance(n_level, int):
        n_level = logging.DEBUG

    if logdict.getboolean('log_to_file', True):
        # Add a rotating logfile handler
        logpath = os.path.join(mupub.CONFIG_DIR,
                               logdict.get('logfilename',
                                           'mupub-errors.log'))
        file_handler = RotatingFileHandler(logpath,
                                           maxBytes=1024*100,
                                           backupCount=3)
        # Logging is always INFO level
        file_handler.setLevel(logging.INFO)
        logform = logging.Formatter(fmt=_FILEFMT,
                                    datefmt=_DATEFMT)
        file_handler.setFormatter(logform)
        mupub_logger.addHandler(file_handler)

    # Console logging is set to the configured level.
    console = logging.StreamHandler()
    console.setLevel(n_level)
    console_form = logging.Formatter(fmt=_CONSOLEFMT,
                                     datefmt=_DATEFMT)
    console.setFormatter(console_form)
    mupub_logger.addHandler(console)


def main():
    """Dispatch with system arguments.

    This private module defines the main entry point for the command
    script. Its function is to define a default file logging mechanism
    for the application and then call :py:func:`dispatch()
    <mupub.cli.dispatch>` to redirect processing to the appropriate
    command.

    More information is available in the :doc:`users-guide`.

    """

    _configure_logging()

    return dispatch(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
