""" Interactions with LilyPond.
"""

__docformat__ = "reStructuredText"

import abc
import logging
import os
import re
import subprocess
import tarfile
import requests
import http.client
from bs4 import BeautifulSoup
from clint.textui import progress
import mupub

# The location of LilyPond categorized binaries
LYCACHE = os.path.join(mupub.CONFIG_DIR, "lycache")
COMPFMT = "lilypond-.*\.sh"
RE_SCRIPT = re.compile("lilypond-([\d\.\-]+)\..*\.sh")
RE_VERSION = re.compile("(\d+)\.(\d+)\.(\d+)(-\d+)?")


def _cached_compilers():
    cache = []
    for folder in os.listdir(LYCACHE):
        if not os.path.isdir(os.path.join(LYCACHE, folder)):
            continue
        if RE_VERSION.match(folder):
            cache.append(folder)
    return cache


_vfact = [100000, 100, 1, 0]


class LyVersion:
    """LilyPond version class.

    This class attempts to simplify version compares so that versions
    can be easily sorted and managed.

    """

    def __init__(self, lp_version):
        self.version = lp_version
        self.sortval = 0
        # remove anything trailing a dash character
        vers = lp_version.split("-")[0]
        n = 0
        for v in vers.split("."):
            self.sortval += int(v) * _vfact[n]
            n += 1

    def is_valid(self):
        """Validity test, must have parsed to an internal sort value."""
        return self.sortval != 0

    def __str__(self):
        return self.version

    def __gt__(self, other):
        """Evaluate this > other using internal integer sortval."""
        return self.sortval > other.sortval

    def __lt__(self, other):
        """Evaluate this < other using internal integer sortval."""
        return self.sortval < other.sortval

    def __eq__(self, other):
        """Evaluate this == other using internal integer sortval."""
        return self.sortval == other.sortval

    def match(self, other):
        """Evaluate this == other using a simple string match."""
        return self.sortval == other.sortval

    def strmatch(self, other):
        """Compare strings, not the internal sort value."""
        return self.version == other.version

    def cache_folder(self):
        """Return path to top of compiler's folder."""
        return os.path.join(LYCACHE, self.version)

    def get_install_script(self, cpu_descr):
        """Retrieve the LilyPond installation script for this processor.

        Gets the name of the script on the LilyPond download
        repository. This routine does not perform download nor the
        installation.

        :param cpu_descr: The name in the appropriate format.
        :returns: A URL using HTTP protocol for the download script,
                  None if not found.
        :rtype: string

        """
        logger = logging.getLogger(__name__)
        if not self.is_valid():
            return None

        # Check download_url then download_url_fallback
        for urltag in [
            "download_url",
            "download_url_fallback",
        ]:
            if urltag not in mupub.CONFIG_DICT["common"]:
                continue
            binurl = mupub.CONFIG_DICT["common"][urltag]
            req = requests.get(binurl)
            if req.status_code != 200:
                continue
            logger.info("Trying %s" % binurl)

            compiler_page = BeautifulSoup(req.content, "html.parser")
            # Find the first link in the page that matches given cpu.
            tlink = compiler_page.find(href=cpu_descr + "/")
            if not tlink:
                continue

            bin_archive = binurl + cpu_descr + "/"
            comp_page = BeautifulSoup(requests.get(bin_archive).content, "html.parser")
            # Filter to get only lilypond install scripts, then search for
            # a match on the version.
            href_re = re.compile(COMPFMT.format(cpu_descr))
            for script in comp_page.find_all(href=href_re):
                script_ref = script.contents[0]
                script_m = RE_SCRIPT.match(script_ref)
                if script_m and self.match(LyVersion(script_m.group(1))):
                    return bin_archive + script_ref

        return None


class LyInstaller(metaclass=abc.ABCMeta):
    """Abstract class, defines protocol for installers."""

    def __init__(self, progress_bar=False):
        self.progress_bar = progress_bar

    @abc.abstractmethod
    def do_install(self, target, lyversion):
        """Perform a LilyPond installation.

        :param target: compiler version to get
        :param bintop: folder in LilyPond binary archives to get
        :returns: True if successful
        """
        return False

    def install(self, lp_version):
        """Concrete front-end to do_install()

        :param lp_version: LilyPond version
        :returns: True if the compiler is already installed.
                  False if lp_version is an invalid version.
                  True if installation completed successfully.

        """
        if not lp_version.is_valid():
            return False

        for folder in _cached_compilers():
            if lp_version == LyVersion(folder):
                return True

        return self.do_install(lp_version)

    def download(self, script_url, output_path):
        """Download an installation script/tarfile

        :param script_url: location of the script
        :param output_path: output path

        """
        request = requests.get(script_url, stream=True)
        print(request.status_code)
        with open(output_path, "wb") as out_script:
            if self.progress_bar:
                total_len = int(request.headers.get("content-length"))
                for chunk in progress.bar(
                    request.iter_content(chunk_size=1024),
                    expected_size=(total_len / 1024) + 1,
                ):
                    if chunk:
                        out_script.write(chunk)
                        out_script.flush()
            else:
                for chunk in request.iter_content(chunk_size=1024):
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
        if cpu_type.endswith("64"):
            cpu_type = "64"

        return sys_info.sysname.lower(), cpu_type


class LinuxInstaller(LyInstaller):

    def __init__(self, progress_bar):
        super().__init__(progress_bar)

    def do_install(self, lyversion):
        """Concrete method of abstract parent.

        Perform a linux install.

        :param lyversion: LilyPond version

        """
        logger = logging.getLogger(__name__)

        install_script = lyversion.get_install_script("-".join(self.system_details()))
        if not install_script:
            logger.warn("No install scripts found for %s" % lyversion.version)
            return False

        local_script = os.path.join(LYCACHE, os.path.basename(install_script))
        logger.info("Downloading build script")
        self.download(install_script, local_script)

        # execute script after downloading
        prefix = "--prefix=" + lyversion.cache_folder()
        command = ["/bin/sh", local_script, "--batch", prefix]
        logger.info("Installing with %s" % prefix)
        try:
            subprocess.check_call(command)
            logger.info("(Linux) Installed %s" % str(lyversion))
            return True
        except subprocess.CalledProcessError as cpe:
            logger.warning("Installation failed, return code=%d" % cpe.returncode)
            return False


class LyLocator:
    """Locate services for LilyPond files.

    This is a factory method that instantiates the appropriate
    installer based on the cpu on which this script is run.

    """

    def __init__(self, lp_version, progress_bar=False):
        self.version = LyVersion(lp_version)
        if not self.version.is_valid():
            raise mupub.BadConfiguration("Bad version (%s)?" % lp_version)

        sys_info = os.uname()
        sysname = sys_info.sysname.lower()
        if sysname in ["linux", "freebsd"]:
            self.app_path = [
                "bin",
                "lilypond",
            ]
            self.installer = LinuxInstaller(progress_bar)
        else:
            # Only linux supported at this time.
            raise mupub.BadConfiguration("%s is not supported" % sysname)

    def working_path(self):
        """Return a path to the appropriate lilypond script.

        This method attempts to resolve the compiler from the local
        cache and, if not found, it will then attempt to install the
        compiler. The current or newly installed compiler path is
        returned.

        :return: path to LilyPond binary for this version or,
                 None if not found.
        :rtype: str, None if working path cannot be determined.

        """
        logger = logging.getLogger(__name__)

        for folder in _cached_compilers():
            candidate = LyVersion(folder)
            if self.version.match(candidate):
                # folder matches this version, return the path to
                # its binary.
                return os.path.join(LYCACHE, folder, *self.app_path)

        # here if there is no match.
        logger.info("Compiler installation needed for %s" % self.version)
        if self.installer.install(self.version):
            return self.working_path()

        return None
