"""mupub initialization and configuration module

Query for configuration parameters, saving them in the config file
when done.

"""

import argparse
import os
import psycopg2
import re
import sqlite3
from clint.textui import prompt, validators, colored, puts
from mupub.config import CONFIG_DICT, CONFIG_DIR, DBPATH, save
from mupub.utils import ConfigDumpAction

# The local database definition: table names and fields.
_TABLES = [
    ('instruments', 'instrument text primary key'),
    ('styles', 'style text primary key'),
    ('composers', 'composer text primary key'),
    ('licenses', 'license text primary key'),
    ('assetmap', """
           folder text,
           name text,
           has_lys integer,
           piece_id integer
    """),
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
driving the web site is used to seed a small local database.
"""

def database_init():
    """Initialize configuration in the database category.

    """
    print(_REMOTE_DESCRIPTION)
    _q_int('remote_db', 'port', 'Database port')
    _q_str('remote_db', 'name', 'Database name')
    _q_str('remote_db', 'user', 'Database user name')
    _q_str('remote_db', 'host', 'Database host')
    _q_str('remote_db', 'password', 'Database password')


def _dbcopy(src_conn, dst_conn, select_q, insert_q):
    with src_conn.cursor() as cursor:
        cursor.execute(select_q)
        for selection in cursor:
            dst_conn.execute(insert_q, selection)


_ASSET_INSERT="""
INSERT OR IGNORE
   INTO assetmap (folder, name, has_lys, piece_id)
   VALUES (?, ?, ?, ?)
"""

def db_sync(local_conn, remote_db):
    db_dict = CONFIG_DICT[remote_db]
    print('connecting to ' + db_dict['host'])
    rem_conn = psycopg2.connect(database=db_dict['name'],
                                user=db_dict['user'],
                                host=db_dict['host'],
                                port=db_dict['port'],
                                password=db_dict['password'],)
    print('connection established')

    with rem_conn:
        print('building assetmap')
        _dbcopy(rem_conn,
                local_conn,
                'SELECT folder,name,has_lys,piece_id FROM mutopia_assetmap',
                ' '.join(re.split('\s+',_ASSET_INSERT)).strip())
        print('building instruments')
        _dbcopy(rem_conn,
                local_conn,
                'SELECT instrument FROM mutopia_instrument',
                'INSERT OR IGNORE INTO instruments (instrument) VALUES (?)')
        print('building styles')
        _dbcopy(rem_conn,
                local_conn,
                'SELECT style FROM mutopia_style',
                'INSERT OR IGNORE INTO styles (style) VALUES (?)')
        print('building composers')
        _dbcopy(rem_conn,
                local_conn,
                'SELECT composer FROM mutopia_composer',
                'INSERT OR IGNORE INTO composers (composer) VALUES (?)')
        print('building licenses')
        _dbcopy(rem_conn,
                local_conn,
                'SELECT name FROM mutopia_license',
                'INSERT OR IGNORE INTO licenses (license) VALUES (?)')


def sync_local_db(remote_db):
    schema_initialized = os.path.exists(DBPATH)
    conn = sqlite3.connect(DBPATH)
    with conn:
        if not schema_initialized:
            for name, fields in _TABLES:
                conn.execute('create table {0} ({1})'.format(
                    name, ''.join(fields).strip()))
        db_sync(conn, remote_db)


def init(dump, database, sync_only):
    """The init entry point.

    Queries for the basic configuration needed to adequately run all
    publishing functions of this application.

    As this is an entry point with its own arguments, all arguments
    are passed into the routine --- as arguments are added, they must
    also be added here.

    :param dump: dump argument was specified and handled by now, the
                 argument is present but not used by this routine.

    """

    if not sync_only:
        try:
            database_init()
            save()
        except KeyboardInterrupt:
            puts(colored.red('\nConfiguration aborted, not saved.'))

    sync_local_db(database)


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
        '--database',
        default='remote_db',
        help='Database to use (defined in config)'
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
