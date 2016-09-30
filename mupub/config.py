""" mupub configuration module
"""

__docformat__ = 'reStructuredText'

import os
import ruamel.yaml as yaml

CONFIG_DIR = os.path.join(os.environ.get('HOME'), '.mupub')
_CONFIG_FNM = os.path.join(CONFIG_DIR, 'config.yml')

_CONFIG_DEFAULT = """
mutopia:
  repo_remote: upstream

remote_db:
  host: mu-devo.chgf8mujp4sf.us-west-2.rds.amazonaws.com
  user: muuser
  name: mudb
  password: ChopinFTW
  port: 5432
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
        tmp_conf = yaml.load(_CONFIG_DEFAULT)
        # set some defaults based on environment
        repo = os.path.join(os.environ.get('HOME'), 'MutopiaProject')
        tmp_conf['mutopia']['local_repo'] = repo
        return tmp_conf


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
