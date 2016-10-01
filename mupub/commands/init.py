"""mupub initialization and configuration module

Query for configuration parameters, saving them in the config file
when done.

"""

import argparse
import os
import sys
import subprocess
from clint.textui import prompt, validators, colored, puts
from mupub.config import CONFIG_DICT, save
from mupub.utils import ConfigDumpAction

def _q_path(category, key, qstr):
    table = CONFIG_DICT[category]
    default = table.get(key, '')
    try:
        val = prompt.query(qstr,
                           default=default,
                           validators=[validators.PathValidator()])
        val = os.path.abspath(val)
        table[key] = val
        return val
    except EOFError:
        print('\n')
        return None


def _q_str(category, key, qstr):
    table = CONFIG_DICT[category]
    default = table.get(key, '')
    try:
        val = prompt.query(qstr, default=default)
        table[key] = val
        return val
    except EOFError:
        print('\n')
        return None


def _q_int(category, key, qstr):
    table = CONFIG_DICT[category]
    default = table.get(key, 0)
    try:
        val = int(prompt.query(qstr,
                               default=str(default),
                               validators=[validators.IntegerValidator()]))
        table[key] = val
        return val
    except EOFError:
        print('\n')
        return None


def _set_remote(path):
    curdir = os.getcwd()
    remotes = []
    try:
        os.chdir(path)
        cmd_output = subprocess.check_output(['git', 'remote'],
                                             universal_newlines=True)
        for rem in cmd_output.split('\n'):
            rem = rem.strip()
            if len(rem) > 0:
                remotes.append(rem)
        remotes.sort()
    finally:
        os.chdir(curdir)

    rem_options = []
    index = 0
    for rem in remotes:
        index += 1
        rem_options.append({'selector': str(index),
                            'prompt': rem,
                            'return': rem})
    try:
        repo_remote = prompt.options('Repo remote to use for fetches',
                                     rem_options)
        CONFIG_DICT['mutopia']['repo_remote'] = repo_remote
    except EOFError:
        print('\n')
        pass


def mutopia_init(debug):
    """Initialize configuration in the mutopia category.

    :param debug: boolean flag

    """
    cur_repo = CONFIG_DICT['mutopia']['local_repo']
    while True:
        path = _q_path('mutopia',
                       'local_repo',
                       'Local repository path')
        if path is None:
            break
        if os.path.exists(os.path.join(path, '.git')):
            break
        else:
            puts(colored.yellow('Enter a valid git repository.'))
            CONFIG_DICT['mutopia']['local_repo'] = cur_repo

    if path is not None:
        _set_remote(path)


def database_init(debug):
    """Initialize configuration in the database category.

    :param debug: boolean flag

    """
    _q_int('database', 'port', 'Database port')
    _q_str('database', 'name', 'Database name')
    _q_str('database', 'user', 'Database user name')
    _q_str('database', 'host', 'Database host')
    _q_str('database', 'password', 'Database password')


def init(debug, dump):
    """The init entry point.

    Queries for specific configution needed to adequately run all
    publishing functions of this application.

    As this is an entry point with its own arguments, all arguments
    are passed into the routine --- as arguments are added, they must
    also be added here.

    :param debug: boolean flag
    :param dump: dump argument was specified and handled by now, the
                 argument is present but not used by this routine.

    """

    try:
        mutopia_init(debug)
        database_init(debug)
        save()
    except KeyboardInterrupt:
        puts(colored.red('\nConfiguration aborted, not saved.'))


def main(args):
    """Module entry point for the init command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub init')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Louder.'
    )
    parser.add_argument(
        '--dump',
        action=ConfigDumpAction,
        nargs=0,
    )
    args = parser.parse_args(args)

    if not args.dump:
        try:
            init(**vars(args))
        except Exception as ex:
            sys.exit('{ex.__class__.__name__} - {ex}'.format(ex=ex))
