""" mupub configuration module
"""

__docformat__ = 'reStructuredText'

import os
import ruamel.yaml as yaml

CONFIG_DIR = os.path.join(os.environ.get('HOME'), '.mupub')
_CONFIG_FNM = os.path.join(CONFIG_DIR, 'config.yml')

"""
site_url: http://127.0.0.1:8000/
"""

_CONFIG_DEFAULT = """
site_url: http://musite-dev.us-west-2.elasticbeanstalk.com/
default_db:
  host: mu-devo.chgf8mujp4sf.us-west-2.rds.amazonaws.com
  user: muuser
  name: mudb
  password: ChopinFTW
  port: 5432

local_db: mu-min-db.db

lilypond:
  V2_8: 2.8.8-1
  V2_10: 2.10.33-1
  V2_12: 2.12.3-1
  V2_14: 2.14.2-1
  V2_16: 2.16.2-1
  V2_17: 2.17.97-1
  V2_18: 2.18.2-1
  V2_19: 2.19.48-1
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
DBPATH = os.path.join(CONFIG_DIR, CONFIG_DICT['local_db'])
