"""A module to localize configuration elements.

A default logging configuration is defined here so that a reasonable
run can be accomplished.

"""

__docformat__ = 'reStructuredText'

import os
import logging
import time
import ruamel.yaml as yaml
import mupub

CONFIG_DIR = os.path.join(os.environ.get('HOME'), '.mupub')
_CONFIG_FNM = os.path.join(CONFIG_DIR, 'config.yml')

class UTCFormatter(logging.Formatter):
    """Set the logging time formatter for UTC.
    """
    converter = time.gmtime

"""
site_url: http://127.0.0.1:8000/
"""

_CONFIG_DEFAULT = """
defaults:
  site_url: http://musite-dev.us-west-2.elasticbeanstalk.com/
  local_db: mu-min-db.db
  download_url: http://download.linuxaudio.org/lilypond/binaries/

# Simple logging to the console
logging:
  version: 1
  disable_existing_loggers: False
  formatters:
    simple:
      format: '%(levelname)s - %(message)s'
  handlers:
    console:
      class: logging.StreamHandler
      formatter: simple
      level: INFO
  root:
    handlers: [console]
"""


def load(config_file=_CONFIG_FNM):
    """Load a configuration file into a dictionary

    :param str config_file: file name from which to load
        configuration.
    :return: configuration data
    :rtype: dict

    """
    try:
        with open(config_file, 'r') as ymlfile:
            return yaml.load(ymlfile, Loader=yaml.RoundTripLoader)
    except FileNotFoundError:
        return yaml.load(_CONFIG_DEFAULT)


def save(config_file=_CONFIG_FNM):
    """Save configuration dictionary to a file.

    :param str config_file: file name in which to save configuration.

    """
    if os.path.dirname(config_file):
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
    if os.path.exists(config_file):
        backup = config_file + '~'
        os.replace(config_file, backup)
    with open(config_file, 'w') as infile:
        yaml.dump(CONFIG_DICT, infile, Dumper=yaml.RoundTripDumper)


# load configuration when imported
CONFIG_DICT = load()

def getDBPath():
    """Return database path from configuration.
    """
    return os.path.join(CONFIG_DIR, CONFIG_DICT['defaults']['local_db'])


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
