"""
This module contains structures to hold LilyPond headers (Header) and
mechanisms (Loaders) to fill them in various ways.

"""
__docformat__ = 'reStructuredText'

import re
import subprocess
import os
import os.path
import logging
from abc import ABCMeta, abstractmethod
import mupub.rdfu

_HEADER_PAT = re.compile(r'\\header', flags=re.UNICODE)
_HTAG_PAT = re.compile(r'\s*(\w+)\s*=\s*\"(.*)\"', flags=re.UNICODE)
_VERSION_PAT = re.compile(r'\s*\\version\s+\"([^\"]+)\"')

REQUIRED_FIELDS = [
    'title',
    'composer',
    'instrument',
    'style',
    'maintainer',
    'source',
]
ADDITIONAL_FIELDS = [
    'lilypondVersion',
    'opus',
    'lyricist',
    'date',
    'metre',
    'arranger',
    'maintainerEmail',
    'maintainerWeb',
    'moreInfo',
]


class Loader(metaclass=ABCMeta):
    """
    A Loader is used to read data from LilyPond files into a hash table.
    This is the base class and interface for all Loaders.

    """

    @abstractmethod
    def load(self, infile):
        """Sub-classes implement the load protocol to fill a key:value
        table.

        :param str infile: input file (specified by subclasses)
        :return: key:value table
        :rtype: dict

        """

        _ = infile
        return {}


    def load_files(self, prefix, files):
        """Load a list of files

        :param str prefix:
        :param str files:

        """
        logger = logging.getLogger(__name__)
        table = {}
        for inf in files:
            inf_path = os.path.join(prefix, inf)
            try:
                table.update(self.load(inf_path))
            except UnicodeDecodeError as err:
                # log and continue
                logger.warning(inf_path +  ' - ' + err)
        return table


class LYLoader(Loader):
    """
    Simple, fast, line-oriented type of Loader for LilyPond files.

    Lines are skipped until the header tag is found, scanning stops
    when the closing brace is found. It reads the key-value pairs and
    returns a hash table containing them.

    Does not handle LilyPond block comments in the header block.

    Raises an InvalidEncoding exception if the file is not properly
    formatted in UTF-8.
    """
    def load(self, infile):
        """Load a LilyPond file

        :param str infile: LilyPond input file
        :returns: table of header key / values
        :rtype: dict

        """
        logger = logging.getLogger(__name__)

        def _net_braces(line):
            return line.count('{') - line.count('}')

        table = {}
        lines = 0
        with open(infile, mode='r', encoding='utf-8') as lyfile:
            lylines = lyfile.readlines()
            net_braces = 0
            header_started = False
            for line in lylines:
                # attempt to discard comments
                line = line.split('%', 1)[0]
                lines += 1
                if not header_started:
                    if _HEADER_PAT.search(line):
                        header_started = True
                        net_braces += _net_braces(line)
                    continue

                hmatch = _HTAG_PAT.search(line)
                if hmatch:
                    table[hmatch.group(1)] = hmatch.group(2)

                # stop processing file at the end of the header
                net_braces += _net_braces(line)
                if net_braces < 1:
                    break
            logger.debug('Header loading discovered %s header lines', lines)

        return table


class VersionLoader(Loader):
    """
    A version loader reads a LilyPond file and builds a table with
    a single entry for the version string.
    """
    def load(self, lyf):
        table = {}
        with open(lyf, mode='r', encoding='utf-8') as lyfile:
            for line in lyfile:
                line = line.split('%', 1)[0]
                vmatch = _VERSION_PAT.search(line)
                if vmatch is not None:
                    table['lilypondVersion'] = vmatch.group(1)
                    # break when found
                    break
        return table


# scheme contributed by DAK
_LILYHDR_SCM = re.sub(r'\s+', ' ', """
(set! print-book-with-defaults
      (lambda (book)
        (module-for-each
         (lambda (sym var)
	   (if (markup? (variable-ref var))
	       (format #t "~a=~S\\n" sym
                   (markup->string (variable-ref var)))))
         (ly:book-header book))))
""")

class SchemeLoader(Loader):
    """Read a lilypond file and read the headers into a dict.
    Load a hash table using LilyPond scheme.

    This routine uses the scheme code developed by David Kastrup and
    Felix Janda to extract header information from the lilypond file.

   :param lilyfile: Filename
   :type lilyfile: string
   :return: dict

    """

    def load(self, lyf):
        if not os.path.isfile(lyf):
            raise FileNotFoundError

        lilycmd = ['lilypond', '-s', '-e',]
        lilycmd.append(''.join(_LILYHDR_SCM).strip())
        lilycmd.append(lyf)
        hdrs = subprocess.check_output(lilycmd, universal_newlines=True)
        hdr_map = {}
        for header_pair in hdrs.split('\n'):
            header_vec = header_pair.split('=', 2)
            if len(header_vec) > 1:
                hdr_map[header_vec[0]] = header_vec[1].strip('" ')

        return hdr_map


class RawLoader(Loader):
    """
    A RawLoader is used to import a file that isn't wrapped
    with a \\header tag and its braces; just a raw set of key:value pairs.

    """
    def load(self, infile):
        table = {}
        with open(infile, mode='r', encoding='utf-8') as lyfile:
            for line in lyfile:
                line = line.split('%', 1)[0]
                htag = _HTAG_PAT.search(line)
                if htag is not None:
                    table[htag.group(1)] = htag.group(2)

        return table


class Header(object):
    """
    A Header contains a table that can be loaded with any type of
    Loader. Once instantiated, multiple calls to loadTable will call
    the loader's ``load()`` method and update the table.

    """

    def __init__(self, loader):
        # initialize all our header fields with blanks
        self._table = {}
        for key in REQUIRED_FIELDS+ADDITIONAL_FIELDS:
            self._table[key] = ''
        self._loader = loader


    def len(self):
        """Return length of header.

        :returns: size of keyword dictionary
        :rtype: int

        """
        return len(self._table)


    def load_table(self, lyf):
        """Update the existing table with another file.

        The given LilyPond file is loaded, adds or overrides the
        existing keywords.

        :param str lyf: LilyPond file to read

        """
        self._table.update(self._loader.load(lyf))


    def load_table_list(self, folder, filelist):
        """Update the existing table with a list of files.

        :param str folder: path name, holds each element of filelist
        :param filelist: a list of files within folder

        """
        self._table.update(self._loader.load_files(folder, filelist))


    def set_field(self, key, value):
        """Set field in table."""
        self._table[key] = value


    def use(self, loader):
        """Switch from one loader to another."""
        self._loader = loader


    def get_field(self, field):
        """Return the value for the given field.

        This provides the Mutopia-ish mechanism of looking up the KEY
        by checking mutopiaKEY first.

        :param str field: key field to look up in table
        :return: value associated with field or None if not found

        """
        val = self.get_value('mutopia' + field)
        if val is not None and len(val) < 1:
            val = None                    # don't allow an empty field
        if val is None:
            val = self.get_value(field)
        if val is not None and len(val) > 0:
            return val
        else:
            return None

    def get_value(self, kwd):
        """Return value associated with kwd.

        This is a raw alternative to get_field().

        :param str kwd: keyword to lookup
        :return: Value of keyword, None if not found

        """
        if kwd in self._table:
            return self._table[kwd]
        return None


    def resolve_license(self):
        for synonym in ['license', 'licence', 'copyright']:
            lic = self.get_field(synonym)
            if lic:
                return lic
        return None


    def is_valid(self):
        """A check for a header validity.

        This is a *quick* validator that only checks that required
        fields are present. It does not check the validity of the
        fields.

        :return: True if the all required fields are present.

        """
        # Return false if any required fields are missing.
        for field in REQUIRED_FIELDS:
            if self.get_field(field) is None:
                return False

        if self.resolve_license() is None:
            return False

        return True


    def write_rdf(self, path, assets=None):
        """Write the RDF to an XML file.

        :param str path: File path to write.
        :param assets: Dictionary block of name:value pairs containing
                       asset names.

        """
        rdf = mupub.MuRDF()
        for rfield in REQUIRED_FIELDS:
            rdf.update_description(rfield, self.get_field(rfield))
        for afield in ADDITIONAL_FIELDS:
            rdf.update_description(afield, self.get_field(afield))

        # special cases
        rdf.update_description('licence', self.resolve_license())
        rdf.update_description('for', self.get_field('instrument'))
        rdf.update_description('id', self.get_field('footer'))

        if assets:
            for name,value in assets.items():
                rdf.update_description(name, value)
        rdf.write_xml(path)


_LILYENDS = ('.ly', '.ily', '.lyi',)
def find_header(relpath, prefix='.'):
    """Get header associated with given path and prefx

    :param relpath: file path, relative to compser to find LilyPond files.
    :return: filled Header object, None if no files found in relpath
    :rtype: Header, None if invalid

    """

    p_to_hdr = os.path.abspath(os.path.join(prefix, relpath))
    if os.path.isdir(p_to_hdr):
        headers = [x for x in os.listdir(p_to_hdr) if x.endswith(_LILYENDS)]
    else:
        headers = [relpath,]
        p_to_hdr = prefix

    hdr = Header(LYLoader())
    hdr.load_table_list(p_to_hdr, headers)

    if not hdr.is_valid():
        # Not found, attempt again with a RawLoader and check files
        # that may be header assignments in a file included from
        # another file.
        hdr.use(RawLoader())
        raw_files = []
        for header in headers:
            if header.lower().startswith(('header', 'mutopia',)):
                raw_files.append(header)
        if len(raw_files) > 0:
            hdr.load_table_list(p_to_hdr, raw_files)

    if hdr.is_valid():
        # The version tag *should* live where the header is found
        hdr.use(VersionLoader())
        hdr.load_table_list(p_to_hdr, headers)
        return hdr

    return None
