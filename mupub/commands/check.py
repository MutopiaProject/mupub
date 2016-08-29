import argparse
import os.path
import sys
from mupub import utils

def check(destination_url):
    print(destination_url)


def main(args):
    parser = argparse.ArgumentParser(prog='mupub check')
    parser.add_argument(
        '--archive_url',
        action=utils.EnvDefault,
        env='MUPUB_ARCHIVE_URL',
        default='http://127.0.0.1:8000/',
        help='The destination URL to which assets will be uploaded.'
    )
    parser.add_argument(
        '--db_url',
        action=utils.EnvDefault,
        env='MUPUB_DB_URL',
        default='http://127.0.0.1:8000/',
        help='The site database.'
    )

    args = parser.parse_args(args)

    try:
        check(**vars(args))
    except Exception as ex:
        sys.exit('{ex.__class__.__name__}: {ex}'.format(ex=ex))
