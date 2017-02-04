"""Utility functions for mupub.
"""
__docformat__ = 'reStructuredText'

import os
import argparse
import sys
from clint.textui.validators import ValidationError
import mupub

def _find_files(folder, outlist):
    for entry in os.scandir(path=folder):
        # ignore hidden and backup files
        if entry.name.startswith('.') or entry.name.endswith('~'):
            continue
        if entry.is_file():
            outlist.append(os.path.join(folder, entry.name))
        elif entry.is_dir():
            # recurse to get files under this folder
            outlist = _find_files(os.path.join(folder, entry.name),
                                  outlist)
    return outlist


def find_files(folder):
    """Return a list of all files in a folder

    :param str folder: The top-most folder.
    :returns: list of files under folder
    :rtype: [str]

    """
    return _find_files(folder, [])


def resolve_input(infile=None):
    """Determine the file naming components for mutopia.

    :param str infile: A candidate input file.
    :returns: base (usually containing folder name) and infile, as
              strings.
    :rtype: Tuple

    A convenience routine to determine the base name for a mutopia
    piece. The mechanism assumes the user's current working directory
    is appropriate to the build being acted on. The algorithm then
    works on the naming convention:

      - If infile==None, determine base and infile from the current
        working directory. This will allow for the possibility of the
        actual files to be in an ``-lys`` subfolder.

      - If infile is given, return the basename of the current working
        folder and infile as a tuple.

    """

    base = os.path.basename(os.getcwd())
    if not infile:
        if os.path.exists(base+'.ly'):
            infile = base+'.ly'
        elif os.path.exists(base+'-lys'):
            candidate = os.path.join(base+'-lys', base+'.ly')
            if os.path.exists(candidate):
                infile = candidate

    return base,infile


class EnvDefault(argparse.Action):
    """Get values from environment variable.

    A custom argparse action that checks the environment for the value
    of an argument in the parser.

    """
    def __init__(self, env, required=True, default=None, **kwargs):
        default = os.environ.get(env, default)
        self.env = env
        if default:
            required = False
        super(EnvDefault, self).__init__(
            default=default,
            required=required,
            **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


_BOOLEANS = {'y': True,
             'yes': True,
             'true': True,
             '1': True,
             'n': False,
             'no': False,
             'false': False,
             '0': False
}


class BooleanValidator(object):
    """A mechanism to validate valid boolean input.
    """

    _message = 'Enter a valid boolean.'

    def __init__(self, message=None):
        if message is not None:
            self._message = message

    def __call__(self, value):
        try:
            return _BOOLEANS[value.strip().lower()]
        except KeyError:
            raise ValidationError(self._message)
