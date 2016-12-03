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
from mupub.config import CONFIG_DICT, CONFIG_DIR, DBPATH, save
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


_REMOTE_DESCRIPTION="""
For the purpose of header verification, portions of the database
driving the web site are used to seed a small local database.
"""

def database_init():
    """Initialize configuration in the database category.

    """
    print(_REMOTE_DESCRIPTION)
    _q_int('default_db', 'port', 'Database port')
    _q_str('default_db', 'name', 'Database name')
    _q_str('default_db', 'user', 'Database user name')
    _q_str('default_db', 'host', 'Database host')
    _q_str('default_db', 'password', 'Database password')


def _dbcopy(src_conn, dst_conn, select_q, insert_q):
    with src_conn.cursor() as cursor:
        cursor.execute(select_q)
        for selection in cursor:
            dst_conn.execute(insert_q, selection)


_INSERT = 'INSERT OR IGNORE INTO {0} ({1}) VALUES (?)'
def _db_sync(local_conn):

    # Use the site's db_hook to request a dump of the minimal values
    # we'll need to do simple verification.
    site = CONFIG_DICT['site_url'].strip()
    if site[len(site)-1] != '/':
        site = site + '/'
    try:
        request = requests.get(site+'db_hook')
        dbdata = request.json()

        for tname,cname in _TABLES:
            for val in dbdata[tname]:
                local_conn.execute(_INSERT.format(tname,cname), (val,))
    except requests.exceptions.ConnectionError as exc:
        puts(colored.red('Failed to connect to %s' % CONFIG_DICT['site_url']))
        puts(colored.red('Fix the site_url config variable in %s' % CONFIG_DIR))
        logger.exception(exc)
        raise exc


def sync_local_db():
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


def init(dump, sync_only):
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
    if not sync_only:
        try:
            database_init()
            save()
        except KeyboardInterrupt:
            puts(colored.red('\nConfiguration aborted, not saved.'))

    sync_local_db()


def main(args):
    """Module entry point for the init command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub init')
    parser.add_argument(
        '--sync-only',
        action='store_true',
        help='Synchronize remote and local databases.'
    )
    parser.add_argument(
        '--dump',
        action=ConfigDumpAction,
        nargs=0,
    )
    args = parser.parse_args(args)

    if not args.dump:
        init(**vars(args))
    #else: dumping is handled in an action routine
