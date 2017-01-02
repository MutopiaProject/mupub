"""Initialization and configuration module.
"""

import argparse
import logging
import os
import re
import requests
import sqlite3
from clint.textui import prompt, validators, colored, puts
import mupub
from mupub.config import CONFIG_DICT, CONFIG_DIR, getDBPath #, save
from mupub.utils import ConfigDumpAction

logger = logging.getLogger(__name__)

# The local database definition: table names and fields, basically
# simple storage as hash tables.
_TABLES = [
    ('instruments', 'instrument'),
    ('styles', 'style'),
    ('composers', 'composer'),
    ('licenses', 'license'),
]

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


def _dbcopy(src_conn, dst_conn, select_q, insert_q):
    with src_conn.cursor() as cursor:
        cursor.execute(select_q)
        for selection in cursor:
            dst_conn.execute(insert_q, selection)


_INSERT = 'INSERT OR IGNORE INTO {0} ({1}) VALUES (?)'
def _db_sync(local_conn):

    # Use the site's db_hook to request a dump of the minimal values
    # we'll need to do simple verification.
    site = CONFIG_DICT['defaults']['site_url'].strip()
    if site[len(site)-1] != '/':
        site = site + '/'
    try:
        request = requests.get(site+'db_hook')
        dbdata = request.json()

        for tname,cname in _TABLES:
            for val in dbdata[tname]:
                local_conn.execute(_INSERT.format(tname,cname), (val,))
    except requests.exceptions.ConnectionError as exc:
        logger.error('Failed to connect to %s' % site)
        logger.warn('Fix the site_url config variable in %s' % CONFIG_DIR)
        raise exc


def _init_config():
    _q_str('defaults',
           'site_url',
           'Full MutopiaProject URL')
    _q_str('defaults',
           'local_db',
           'Local (SQLite3) database path')
    for k in CONFIG_DICT['lilypond'].keys():
        _q_str('lilypond', k, 'Compiler for LilyPond '+k)


def _init_db():
    db_path = getDBPath()
    schema_initialized = os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            if not schema_initialized:
                for name, fields in _TABLES:
                    conn.execute('CREATE TABLE {0} ({1} TEXT PRIMARY KEY)'.format(
                        name,
                        ''.join(fields).strip()))
            _db_sync(conn)
    except Exception as exc:
        logger.warning('Exception caught, rolling back changes.')
        logger.exception('In sync_local_db: %s', exc)


def init(dump, sync_only):
    """The init entry point.

    :param dump: If specified, it is handled by an argparse action
        routine and so is ignored here.

    :param sync_only: Only synchronize the database with the
        configured server.

    This command should be executed before any builds or checks.

    Init queries for the basic configuration needed to adequately run
    all publishing functions of this application. The default path for
    the configuration parameter file is ``$HOME/.mupub/config.yml``.
    If that folder doesn't exist, it is created.

    The configuration folder will be used to store the cache of
    |LilyPond| compilers as well as a small database used for
    verification. This database is updated by requesting information
    from the URL from the site specified in the configuration.

    Init can be run at any time. If a database is already present it
    is updated with current data (composers, instruments, etc.) from
    the website.

    """

    # As this is an entry point with its own arguments, all arguments
    # are passed into the routine --- as arguments are added, they must
    # also be added here.

    logger.info('init command starting.')
    try:
        if not sync_only:
            _init_config()
            mupub.config.save()
        _init_db()
        return True
    except KeyboardInterrupt:
        pass
    return False


def verify_init():
    """Verify configuration.

    :returns: True if a valid configuration exists, False otherwise.
    :rtype: boolean

    Tests the configuration and prompts you to run an :py:func:`init`
    command. This is a public routine that may be called from other
    commands to check the validity of installation.

    """

    try:
        mupub.test_config()
        return True
    except mupub.BadConfiguration:
        # Handled expected exception
        logging.warn('You need to run the init command before continuing.')

    try:
        do_init = prompt.query('Initialize now?',
                               default='no',
                               validators=[mupub.utils.BooleanValidator()])
    except KeyboardInterrupt:
        puts(colored.yellow('\nFine, but you will need to initialize eventually.'))
        return False

    if do_init:
        return init(False)

    return False


def main(args):
    """Module entry point for the init command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub init')
    parser.add_argument(
        '--dump',
        action=ConfigDumpAction,
        nargs=0,
        help='Print configuration and exit.',
    )
    parser.add_argument(
        '--sync-only',
        action='store_true',
        help='Perform only the database update',
    )
    args = parser.parse_args(args)

    if not args.dump:
        init(**vars(args))
    #else: dumping is handled in an action routine
