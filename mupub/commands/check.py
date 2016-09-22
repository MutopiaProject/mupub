import argparse
import os
import sys
import psycopg2
import mupub
from mupub.config import config_dict

def _valid_composer(conn, composer):
    try:
        cur = conn.cursor()
        cur.execute('select count(*) from mutopia_composer where composer=%s;',
                    (composer,))
        (count,) = cur.fetchone()
        if count != 1:
            print('composer "{}" is not valid'.format(composer))
            return False
    finally:
        cur.close()
    return True


def _valid_style(conn, style):
    try:
        cur = conn.cursor()
        cur.execute('select count(*) from mutopia_style where style=%s',
                    (style,))
        (count,) = cur.fetchone()
        if count != 1:
            print('style "{}" is not valid'.format(style))
            return false
    finally:
        cur.close()
    return True


def _valid_license(conn, license):
    try:
        cur = conn.cursor()
        cur.execute('select count(id) from mutopia_license where name=%s',
                    (license,))
        (count,) = cur.fetchone()
        if count != 1:
            print('license "{}" is not valid'.format(license))
            return false
    finally:
        cur.close()
    return True


def _basic_checks(header):
    required_fields = ['title',
                       'composer',
                       'instrument',
                       'source',
                       'style',
                       'maintainer',
                       'lp_version',]
    failed_count = 0
    for required_field in required_fields:
        item = header.get_field(required_field)
        if not item:
            print('missing header keyword: {}'.format(required_field))
            failed_count += 1

    # license check is done separately to accomodate for copyright
    # synonym.
    if header.get_field('copyright'):
        print('copyright will be updated to license')
        header.set_field('license', header.get_field('copyright'))
    else:
        if not header.get_field('license'):
            print('no license or copyright found')
            failed_count += 1

    return failed_count


def _load_complete_header(lyfile):
    if os.path.isdir(lyfile):
        print('searching all of {} for header'.format(lyfile))
        return mupub.find_header(lyfile, '.')
    else:
        ly_header = mupub.Header(mupub.LYLoader())
        ly_header.load_table(lyfile)
        ly_header.use(mupub.VersionLoader())
        ly_header.load_table(lyfile)
        return ly_header


def validate(header):
    fails = _basic_checks(header)
    if  fails > 0:
        print('basic checks failed, stopping now.')
        return fails

    db_dict = config_dict['local_db']
    fails = 0
    try:
        conn = psycopg2.connect(database=db_dict['db_name'],
                                user=db_dict['user'],
                                host=db_dict['host'],
                                port=db_dict['port'],
                                password=db_dict['db_password'],
        )
        if not _valid_composer(conn, header.get_field('composer')):
            fails += 1
        if not _valid_style(conn, header.get_field('style')):
            fails += 1
        if not _valid_license(conn, header.get_field('license')):
            fails += 1
    finally:
        conn.close()

    return fails


def check(infile, debug=False):
    header = _load_complete_header(infile)
    if not header:
        print('failed to find header')
        return
    failure_count = validate(header)
    if failure_count > 0:
        print('{} failed one or more validations'.format(infile))
    else:
        lp_version = header.get_value('lp_version')
        print('{} is valid'.format(infile))
        print('This file uses LilyPond version '
              + header.get_value('lp_version'))
        path = mupub.working_path(lp_version)
        if not path:
            print('No appropriate compiler found.')
            path = mupub.install_lily_binary(lp_version)

        # Path could still be None if the compiler wasn't found or the
        # installation failed.
        if path:
            print('Will use compiler at ' + path)


def main(args):
    parser = argparse.ArgumentParser(prog='mupub check')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='play louder'
    )
    parser.add_argument(
        'infile',
        nargs='?',
        help='lilypond file to check'
    )

    args = parser.parse_args(args)

    try:
        check(**vars(args))
    except Exception as ex:
        sys.exit('{ex.__class__.__name__} - {ex}'.format(ex=ex))
