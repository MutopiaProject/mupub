"""Initialization and configuration module.
"""

import argparse
import logging
import os
import sqlite3
import sys
import urllib.parse
from bs4 import BeautifulSoup
import requests
import re
from clint.textui import prompt, validators, colored, puts
import mupub


def _q_str(category, key, qstr):
    table = mupub.CONFIG_DICT[category]
    default = table.get(key, '')
    try:
        val = prompt.query(qstr, default=default)
        table[key] = val
        return val
    except EOFError:
        print('\n')
        return None


def _q_int(category, key, qstr):
    table = mupub.CONFIG_DICT[category]
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


# Licenses are not available from datafiles so they are initialized
# with these values. See _db_sync().
_LICENSES = [
    'Creative Commons Attribution 2.5',
    'Creative Commons Attribution 3.0',
    'Creative Commons Attribution 4.0',
    'Creative Commons Attribution-ShareAlike',
    'Creative Commons Attribution-ShareAlike 2.0',
    'Creative Commons Attribution-ShareAlike 2.5',
    'Creative Commons Attribution-ShareAlike 3.0',
    'Creative Commons Attribution-ShareAlike 4.0',
    'Public Domain',
]

# The local database definition, tuples are (table-name,key-name):
_TABLES = [
    ('instruments', 'instrument'),
    ('styles', 'style'),
    ('composers', 'composer'),
    ('licenses', 'license'),
]

_INSERT = 'INSERT OR IGNORE INTO {0} ({1}) VALUES (?)'

_CREATE_TRACKER = """CREATE TABLE IF NOT EXISTS
   id_tracker (
      piece_id INT PRIMARY KEY,
      pending INT DEFAULT 1
   )
"""
def _update_tracker(conn):
    logger = logging.getLogger(__name__)
    common = mupub.CONFIG_DICT['common']

    logger.info('Looking at %s' % common['mutopia_url'])
    url = urllib.parse.urljoin(common['mutopia_url'],
                               'latestadditions.html')
    req = requests.get(url)
    latest_page = BeautifulSoup(req.content, 'html.parser')
    plist = latest_page.find_all(href=re.compile('piece-info\.cgi'))
    # Build a list of current ids
    idlist = []
    for ref in plist:
        href = urllib.parse.urlparse(ref.get('href'))
        if href.query:
            for q in urllib.parse.parse_qsl(href.query):
                if q[0] == 'id':
                    idlist.append(q[1])

    cursor = conn.cursor()
    last_piece = (max(idlist),)
    # Remove anything older than the latest piece id (but keep latest)
    cursor.execute('DELETE FROM id_tracker WHERE piece_id < ?', last_piece)
    # Mark the latest on the server as pending
    cursor.execute('UPDATE id_tracker set pending=0 WHERE piece_id = ?', last_piece)
    # Finally, log the pendings as INFO
    cursor.execute('SELECT piece_id FROM id_tracker WHERE pending')
    for row in cursor.fetchall():
        logger.info('%d is pending' % row)

    # We want at least one row in the table, which may happen on the
    # first initialization.
    cursor.execute('select count(piece_id) from id_tracker')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO id_tracker (piece_id,pending) VALUES (?,0)', last_piece)


def _db_update(conn, datadir, target, table_name=None):
    if not table_name:
        table_name = target+'s'
    with open(os.path.join(datadir, table_name+'.dat'), 'r') as infile:
        cursor = conn.cursor()
        sql_insert = _INSERT.format(table_name, target)
        for line in infile:
            cursor.execute(sql_insert, (line.strip(),))
            _ = infile.readline() # toss description line


def _db_sync(local_conn):
    logger = logging.getLogger(__name__)

    lice_insert = _INSERT.format('licenses','license')
    for lice in _LICENSES:
        local_conn.execute(lice_insert, (lice,))
    datadir = os.path.expanduser(mupub.CONFIG_DICT['common']['datafiles'].strip())
    _db_update(local_conn, datadir, 'composer')
    _db_update(local_conn, datadir, 'style')
    _db_update(local_conn, datadir, 'instrument')
    _update_tracker(local_conn)


_CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS {0} ({1} TEXT PRIMARY KEY)'
def _init_db():
    logger = logging.getLogger(__name__)
    db_path = mupub.getDBPath()
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            for name, fields in _TABLES:
                conn.execute(_CREATE_TABLE.format(name, ''.join(fields).strip()))
            # Create table to track id prediction
            conn.execute(_CREATE_TRACKER)
            _db_sync(conn)
    except Exception as exc:
        logger.warning('Exception caught, rolling back changes.')
        logger.exception('In sync_local_db: %s', exc)


def _init_config():
    _q_str('common',
           'datafiles',
           'Location of MutopiaWeb project datafiles')
    _q_str('common',
           'repository',
           'Location of local MutopiaProject git repository')
    # This probably doesn't have to be a query, but a check should be
    # made since this table entry wasn't present in alpha releases.
    common = mupub.CONFIG_DICT['common']
    if 'mutopia_url' not in common:
        common['mutopia_url'] = 'http://www.mutopiaproject.org/'


def init(dump, sync_only):
    """The init entry point.

    :param dump: If specified, it is handled by an argparse action
        routine and so is ignored here.
    :param sync_only: Only synchronize the database with the
        configured server.

    This command should be executed before any builds or checks.

    Init queries for the basic configuration needed to adequately run
    all publishing functions of this application. The default path for
    the configuration parameter file is ``$HOME/.mupub/config.cfg``.
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

    logger = logging.getLogger(__name__)
    try:
        if not sync_only:
            _init_config()
            mupub.saveConfig()
            logger.info('configuration saved')
        logger.info('starting initialization')
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

    logger = logging.getLogger(__name__)
    try:
        mupub.test_config()
        return True
    except mupub.BadConfiguration:
        # Handled expected exception
        puts(colored.red('You need to run the init command before continuing.'))

    try:
        do_init = prompt.query('Initialize now?',
                               default='no',
                               validators=[mupub.utils.BooleanValidator()])
    except (KeyboardInterrupt, EOFError):
        do_init = False

    if do_init:
        return init(False, False)
    else:
        puts(colored.yellow('\nFine, but you will need to initialize eventually.'))

    return False


def main(args):
    """Module entry point for the init command.

    :param args: unparsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(prog='mupub init')
    parser.add_argument(
        '--dump',
        action='store_true',
        help='Print configuration and exit.',
    )
    parser.add_argument(
        '--sync-only',
        action='store_true',
        help='Perform only the database update',
    )
    args = parser.parse_args(args)

    if args.dump:
        mupub.CONFIG_DICT.write(sys.stdout)
    else:
        init(**vars(args))
