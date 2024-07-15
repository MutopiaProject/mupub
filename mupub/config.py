"""A module to localize configuration elements.

A default logging configuration is defined here so that a reasonable
run can be accomplished.

"""

__docformat__ = "reStructuredText"

import os
import logging
import configparser
import mupub

CONFIG_DIR = os.path.expanduser("~/.mupub")
_CONFIG_FNM = os.path.join(CONFIG_DIR, "mu-config.cfg")

_CONFIG_DEFAULT = """
[common]
  datafiles = ~/MutopiaWeb/datafiles
  repository = ~/MutopiaProject
  local_db = mu-min-db.db
  download_url = http://download.linuxaudio.org/lilypond/binaries/
  download_url_fallback = http://lilypond.org/downloads/binaries/
  mutopia_url = http://www.mutopiaproject.org/
  preview_fnm = preview.svg
[logging]
  log_to_file = True
  logfilename = mupub-errors.log
  loglevel = INFO
"""

# This is a hack to add new keys to the configuration.
_new_common = {
    "download_url_fallback": "http://lilypond.org/downloads/binaries/",
}


def _configure():
    # A null handler is added to quite the internal logging for simple
    # library usage. See :py:func:`__main__() <mupub.__main__>` for
    # how loggers are added for command-line purposes.
    logging.getLogger("mupub").addHandler(logging.NullHandler())
    config_dirty = False

    # On the first use, a default configuration is added in the user's
    # home folder.
    config = configparser.RawConfigParser()
    if not os.path.isdir(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)
    if os.path.exists(_CONFIG_FNM):
        config.read_file(open(_CONFIG_FNM))

    else:
        config.read_string(_CONFIG_DEFAULT)
        config_dirty = True

    # Check for new keys so they can be slipped in to help the user
    for ckey in iter(_new_common):
        if ckey not in config["common"]:
            config["common"][ckey] = _new_common[ckey]
            config_dirty = True

    if config_dirty:
        with open(_CONFIG_FNM, "w") as configfile:
            config.write(configfile, space_around_delimiters=True)

    return config


# load configuration on import
CONFIG_DICT = _configure()


def saveConfig():
    """Convenience routine to save the configuration."""
    with open(_CONFIG_FNM, "w") as configfile:
        CONFIG_DICT.write(configfile, space_around_delimiters=True)


def getDBPath():
    """Return database path from configuration."""
    return os.path.join(CONFIG_DIR, CONFIG_DICT["common"]["local_db"])


def test_config():
    """Test that a minimally valid configuration exists.

    :return: True on good configuration, False otherwise.

    """
    if not os.path.exists(CONFIG_DIR):
        raise mupub.BadConfiguration("Configuration folder not found.")
    if not os.path.exists(_CONFIG_FNM):
        raise mupub.BadConfiguration("Configuration file not found.")
    if not os.path.exists(getDBPath()):
        raise mupub.BadConfiguration("Local database not found.")
    if len(CONFIG_DICT) == 0:
        raise mupub.BadConfiguration("Configuration was not loaded.")
