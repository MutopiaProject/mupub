"""A module to localize configuration elements.

A default logging configuration is defined here so that a reasonable
run can be accomplished.

"""

__docformat__ = 'reStructuredText'

import os
import logging
import time
import configparser
import mupub

class UTCFormatter(logging.Formatter):
    """Set the logging time formatter for UTC.
    """
    converter = time.gmtime

CONFIG_DIR = os.path.join(os.environ.get('HOME'), '.mupub')
_CONFIG_FNM = os.path.join(CONFIG_DIR, 'config.cfg')

_CONFIG_DEFAULT = """
[common]
  site_url = http://musite-dev.us-west-2.elasticbeanstalk.com/
  local_db = mu-min-db.db
  download_url = http://download.linuxaudio.org/lilypond/binaries/

[loggers]
  keys = root,simple

[handlers]
  keys = consoleHandler

[formatters]
  keys = simpleFormatter

[logger_root]
  level = DEBUG
  handlers = consoleHandler

[logger_simple]
  level = INFO
  handlers = consoleHandler

[handler_consoleHandler]
  class = StreamHandler
  level = INFO
  formatter = simpleFormatter
  args = (sys.stdout,)

[formatter_simpleFormatter]
  format = %(levelname)s - %(message)s
  datefmt = UTCFormatter
"""

def _configure():
    config = configparser.RawConfigParser()
    if not os.path.isdir(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)
    if os.path.exists(_CONFIG_FNM):
        config.read_file(open(_CONFIG_FNM))
    else:
        config.read_string(_CONFIG_DEFAULT)
        with open(_CONFIG_FNM, 'w') as configfile:
            config.write(configfile,
                         space_around_delimiters=True)

    return config


# load configuration on import
CONFIG_DICT = _configure()


def saveConfig():
    """Convenience routine to save the configuration.
    """
    with open(_CONFIG_FNM, 'w') as configfile:
        CONFIG_DICT.write(configfile,
                          space_around_delimiters=True)


def getDBPath():
    """Return database path from configuration.
    """
    return os.path.join(CONFIG_DIR, CONFIG_DICT['common']['local_db'])


def test_config():
    """Test that a minimally valid configuration exists.

    :return: True on good configuration, False otherwise.

    """
    if not os.path.exists(CONFIG_DIR):
        raise mupub.BadConfiguration('Configuration folder not found.')
    if not os.path.exists(_CONFIG_FNM):
        raise mupub.BadConfiguration('Configuration file not found.')
    if not os.path.exists(getDBPath()):
        raise mupub.BadConfiguration('Local database not found.')
    if len(CONFIG_DICT) == 0:
        raise mupub.BadConfiguration('Configuration was not loaded.')
