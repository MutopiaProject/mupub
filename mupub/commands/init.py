"""mupub initialization and configuration module

Query for configuration parameters, saving them in the config file
when done.

"""

import argparse
import logging
import os
import re
import requests
import sqlite3
from clint.textui import prompt, validators, colored, puts
import mupub
from mupub.config import CONFIG_DICT, CONFIG_DIR, DBPATH #, save
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
        puts(colored.red('Failed to connect to %s' % site))
        puts(colored.red('Fix the site_url config variable in %s' % CONFIG_DIR))
        logger.exception(exc)
        raise exc


def init_config():
    _q_str('defaults',
           'site_url',
           'Full MutopiaProject URL')
    _q_str('defaults',
           'local_db',
           'Local (SQLite3) database path')
    for k in CONFIG_DICT['lilypond'].keys():
        _q_str('lilypond', k, 'Compiler for LilyPond '+k)


def init_db():
    schema_initialized = os.path.exists(DBPATH)
    conn = sqlite3.connect(DBPATH)
    try:
        with conn:
            if not schema_initialized:
                for name, fields in _TABLES:
                    conn.execute('CREATE TABLE {0} ({1} TEXT PRIMARY KEY)'.format(
                        name,
                        ''.join(fields).strip()))
            _db_sync(conn)
    except Exception as exc:
        puts(colored.yellow('Exception caught, rolling back changes.'))
        puts(colored.yellow('Exception was %s' % exc))
        logger.exception('In sync_local_db: %s', exc)


def init(dump):
    """The init entry point.

    Queries for the basic configuration needed to adequately run all
    publishing functions of this application.

    As this is an entry point with its own arguments, all arguments
    are passed into the routine --- as arguments are added, they must
    also be added here.

    :param dump: dump argument was specified and handled by now, the
                 argument is present but not used by this routine.

    """
    logger.debug('init command starting.')
    try:
        init_config()
        init_db()
        mupub.config.save()
    except KeyboardInterrupt:
        pass


def verify_init():
    try:
        mupub.test_config()
        return
    except mupub.BadConfiguration:
        # Handled expected exception
        puts(colored.red('Initialization required to continue'))

    try:
        do_init = prompt.query('Initialize now?',
                               default='no',
                               validators=[mupub.utils.BooleanValidator()])
    except KeyboardInterrupt:
        puts(colored.yellow('\nFine, but you will need to initialize eventually.'))
        return False

    if do_init:
        puts(colored.green('Starting initialization'))
        init(False)
        return True
    else:
        puts(colored.yellow('You will need to init to continue.'))

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
    )
    args = parser.parse_args(args)

    if not args.dump:
        init(**vars(args))
    #else: dumping is handled in an action routine
