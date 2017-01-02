"""The main console script entry point.

"""

import logging
from logging.config import dictConfig
import os.path
import sys
from mupub.cli import dispatch
from mupub import CONFIG_DICT, UTCFormatter, CONFIG_DIR
from logging.handlers import RotatingFileHandler

_LOGFORMAT = '%(asctime)s - %(name)s %(levelname)s - %(message)s'
_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

def main():
    """Dispatch with system arguments.

    This private module defines the main entry point for the command
    script. Its function is to define a default file logging mechanism
    for the application and then call :py:func:`dispatch()
    <mupub.cli.dispatch>` to redirect processing to the appropriate
    command.

    More information is available in the :doc:`users-guide`.

    """

    # load the deafult logging from the config file
    if 'logging' in CONFIG_DICT:
        dictConfig(CONFIG_DICT['logging'])

    # add a logfile handler
    logger = logging.getLogger('mupub')
    logpath = os.path.join(CONFIG_DIR, 'mupub-errors.log')
    rotating_handler = RotatingFileHandler(logpath,
                                           maxBytes=1024*100,
                                           backupCount=3)
    formatter = logging.Formatter(fmt=_LOGFORMAT, datefmt=_DATEFORMAT)
    rotating_handler.setFormatter(formatter)
    rotating_handler.setLevel(logging.DEBUG)
    logger.addHandler(rotating_handler)

    return dispatch(sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
