""" Interactions with LilyPond
"""

import os
import re
import requests
import subprocess
from clint.textui import progress
from mupub.config import CONFIG_DIR

LYCACHE = os.path.join(CONFIG_DIR, 'lycache')

class LyVersion():
    def __init__(self, lp_version):
        self.version = lp_version
        v_vec = lp_version.split('.',2)
        try:
            self.sortval = int(v_vec[0])*100 + int(v_vec[1])
        except ValueError:
            self.sortval = 0

    def __str__(self):
        return self.version

    def __gt__(self, other):
        return self.sortval > other.sortval

    def __eq__(self, other):
        return self.sortval == other.sortval


def working_path(lp_version):
    """ Return a path to the appropriate lilypond script.

    :param str lp_version: LilyPond version string from .ly file
    :return:

    """

    ly_version = LyVersion(lp_version)
    vlist = [LyVersion(x) for x in os.listdir(LYCACHE)
             if os.path.isdir(os.path.join(LYCACHE, x))]
    version_path = None
    for version in vlist:
        if version == ly_version:
            version_path = os.path.join(LYCACHE,
                                        str(version),
                                        'bin',
                                        'lilypond')
            break

    return version_path


def _run_install_script(fnm):
    m = re.search('lilypond-([\.0-9]+-[\d+])', fnm)
    if not m:
        # throw exception here?
        print('could not determine prefix from ' + fnm)
        return
    print('Attempting installation.')
    prefix = '--prefix=' + os.path.join(LYCACHE, m.group(1))
    command = ['/bin/sh', fnm, '--batch', prefix]
    subprocess.run(command, shell=False)

    
def install_lily_binary(lp_version):
    """ Find an appropriate lilypond installation script.

    :param str lp_version: LilyPond version string from .ly file
    """

    # Put these in configuration somewhere?
    BINURL = 'http://download.linuxaudio.org/lilypond/binaries'
    version_table = { '2.8': '2.8.8-1',
                      '2.10': '2.10.33-1',
                      '2.12': '2.12.3-1',
                      '2.14': '2.14.2-1',
                      '2.16': '2.16.2-1',
                      '2.17': '2.17.97-1',
                      '2.18': '2.18-2-1',
                      '2.19': '2.19-48-1',
    }

    # First order of business is to see if we can resolve this
    # compiler version.
    vkey = '.'.join(lp_version.split('.')[:2])
    if vkey not in version_table:
        print('There is no available compiler for this version.')
        print('Run convert-ly on this transcription.')
        return

    # cpu_type needs to be one of,
    #   64, x86, arm, ppc
    sys_info = os.uname()
    cpu_type = sys_info.machine
    # 64-bit linux returns x86_64
    if cpu_type.endswith('64'):
        cpu_type = '64'

    bintop = '{0}-{1}'.format(sys_info.sysname.lower(), cpu_type)
    binscript = 'lilypond-{0}.{1}.sh'.format(version_table[vkey], bintop)
    script_url = '/'.join([BINURL, bintop, binscript])

    # Get the shell script in a binary stream.
    print('getting ' + script_url)
    r = requests.get(script_url, stream=True)
    script_fnm = os.path.join(LYCACHE, binscript)
    with open(script_fnm, 'wb') as out_script:
        total_len = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024),
                                  expected_size=(total_len/1024) + 1):
            if chunk:
                out_script.write(chunk)
                out_script.flush()

    _run_install_script(script_fnm)
