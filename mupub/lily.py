""" Interactions with LilyPond
"""

__docformat__ = 'reStructuredText'

import abc
import os
import subprocess
import tarfile
import requests
from clint.textui import progress, colored, puts
import mupub

# The location of LilyPond categorized binaries
LYCACHE = os.path.join(mupub.CONFIG_DIR, 'lycache')

BINURL = 'http://download.linuxaudio.org/lilypond/binaries'
"""
From the README at this site:

darwin-ppc - MacOS X powerpc
darwin-x86 - MacOS X intel
freebsd-64 - FreeBSD 6.x, x86_64
freebsd-x86 - FreeBSD 4.x, x86
linux-64 - Any GNU/Linux distribution, x86_64
linux-arm - Any GNU/Linux distribution, arm
linux-ppc - Any GNU/Linux distribution, powerpc
linux-x86 - Any GNU/Linux distribution, x86
mingw - Windows x86

"""

class LyVersion():
    """LilyPond version class.

    This class attempts to simplify version compares so that versions
    can be easily sorted and managed.

    """
    def __init__(self, lp_version):
        self.version = lp_version
        v_vec = lp_version.split('.', 2)
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

    def matches(self, other):
        """Check for match against another LyVersion object."""
        return self.sortval == other.sortval

    def full_match(self, other):
        """String equality to the version itself."""
        return self.version == other.version


class LyInstaller(metaclass=abc.ABCMeta):
    """Abstract class, defines protocol for installers.
    """

    @abc.abstractmethod
    def do_install(self, target, bintop):
        """Perform a LilyPond installation.

        :param target: compiler version to get
        :param bintop: folder in LilyPond binary archives to get

        """
        pass


    def install(self, lp_version):
        """Concrete front-end to do_install()

        :param lp_version: LilyPond version

        """
        target = self.compiler_target(lp_version)
        if not os.path.exists(os.path.join(LYCACHE, target)):
            sysname, cpu_type = self.system_details()
            self.do_install(target, '{0}-{1}'.format(sysname, cpu_type))


    @classmethod
    def compiler_target(cls, lp_version):
        """Return the compiler configured for the given LilyPond
        version.

        Given a LilyPond version (major.minor.release-number), find
        the compiler configured for that *set* of releases for
        ``major.minor``. It may not be a release matching the input.
        For example, if the system is configured for the 2.19.48-1
        compiler, an input of 2.19.32-1 will return 2.19.48-1.

        The goal is to have all 2.19.*-* files compiled with a single
        compiler.

        :param lp_version: version to look up
        :returns: LilyPond version string
        :rtype: str

        """
        # First order of business is to see if we can resolve this
        # compiler version.
        vkey = 'V' + '_'.join(str(lp_version).split('.')[:2])
        if vkey not in mupub.CONFIG_DICT['lilypond']:
            raise mupub.BadConfiguration(vkey + ' cannot be matched, check configuration.')
        return mupub.CONFIG_DICT['lilypond'][vkey]


    @classmethod
    def download(cls, script_url, output_path):
        """Download an installation script/tarfile

        :param script_url: location of the script
        :param output_path: output path

        """
        request = requests.get(script_url, stream=True)
        with open(output_path, 'wb') as out_script:
            total_len = int(request.headers.get('content-length'))
            for chunk in progress.bar(request.iter_content(chunk_size=1024),
                                      expected_size=(total_len/1024) + 1):
                if chunk:
                    out_script.write(chunk)
                    out_script.flush()


    # cpu_type needs to be one of,
    #   64, x86, arm, ppc
    @classmethod
    def system_details(cls):
        """Return system info needed for installation.

        :returns: The name and cpu type to match the running machine.
        :rtype: tuple (name, cpu-type)

        """
        sys_info = os.uname()
        cpu_type = sys_info.machine
        # 64-bit linux returns x86_64
        if cpu_type.endswith('64'):
            cpu_type = '64'

        return sys_info.sysname.lower(), cpu_type


class LinuxInstaller(LyInstaller):

    def do_install(self, target, bintop):
        """Concrete method of abstract parent.

        Perform a linux install.

        :param target: LilyPond version
        :param bintop: Remote folder reference

        """
        binscript = 'lilypond-{0}.{1}.sh'.format(target, bintop)
        local_script = os.path.join(LYCACHE, binscript)
        puts(colored.yellow('downloading build script'))
        self.download('/'.join([BINURL, bintop, binscript,]),
                      local_script)
        # execute script after downloading
        prefix = '--prefix=' + os.path.join(LYCACHE, target)
        command = ['/bin/sh', local_script, '--batch', prefix]
        puts(colored.yellow('installing ...'))
        subprocess.run(command, shell=False)
        puts(colored.yellow('Done. First run will initialize font tables.'))


class MacInstaller(LyInstaller):

    def do_install(self, target, bintop):
        """Concrete method of abstract parent.

        Perform a Mac install.

        :param target: LilyPond version
        :param bintop: Remote folder reference

        """
        bintar = 'lilypond-{0}.{1}.tar.bz2'.format(target, bintop)
        local_tar = os.path.join(LYCACHE, bintar)
        self.download('/'.join([BINURL, bintop, bintar]), local_tar)

        # extract after downloading
        with tarfile.open(local_tar, mode='r:bz2') as tar_f:
            tar_f.extractall(path=os.path.join(LYCACHE, target))


class LyLocator():
    """Locate services for LilyPond files.

    Requesting the working path may attempt a LilyPond installation.
    """
    def __init__(self, lp_version):
        self.version = LyVersion(lp_version)
        sys_info = os.uname()
        sysname = sys_info.sysname.lower()
        if sysname in ['linux', 'freebsd']:
            self.app_path = ['bin', 'lilypond',]
            self.installer = LinuxInstaller()
        elif sysname == 'darwin':
            self.app_path = ['LilyPond.app',
                             'Contents',
                             'Resources',
                             'bin',]
            self.installer = MacInstaller()
        else:
            raise mupub.BadConfiguration(sysname + ' is not supported')


    def working_path(self):
        """ Return a path to the appropriate lilypond script.

        :return: path to LilyPond binary for this version or,
                 None if not found.
        :rtype: str

        """

        for folder in os.listdir(LYCACHE):
            if os.path.isdir(os.path.join(LYCACHE, folder)):
                candidate = LyVersion(folder)
                if candidate.matches(self.version):
                    # folder matches this version, return the path to
                    # its binary.
                    return os.path.join(LYCACHE, folder, *self.app_path)

        # here if there is no match.
        self.installer.install(self.version)

        # recurse after installation to get path
        return self.working_path()
