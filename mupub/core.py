"""Core routines for the mutopia utilities library.
"""

__docformat__ = "reStructuredText"

import os
import re
import datetime
from stat import S_ISDIR

# mutopia base variable is set to "$HOME/Mutopia" if MUTOPIA_BASE not
# set.
MUTOPIA_BASE = os.getenv("MUTOPIA_BASE", os.path.join(os.getenv("HOME"), "Mutopia"))
FTP_BASE = os.path.join(MUTOPIA_BASE, "ftp")
URL_BASE = "http://www.mutopiaproject.org"


_FOOT_PAT = re.compile("Mutopia-([0-9/]+)-([0-9]+)")


def id_from_footer(footer, strict=True):
    """Parse the footer containing the mutopia id.

    :param str footer: The footer element from the |LilyPond| header.
    :returns: publish date and mutopia id parsed from footer.
    :rtype: tuple, (date, id)
    :throws: ValueError if invalid date

    """
    if not footer:
        raise ValueError("Empty footer")

    fmat = _FOOT_PAT.search(footer)
    if fmat:
        (year, month, day) = fmat.group(1).split("/")
        date = datetime.date(int(year), int(month), int(day))
        its_id = 0
        try:
            its_id = int(fmat.group(2))
        except ValueError as ve:
            # handle caught exception
            if strict:
                raise ve("Failed strict Mutopia ID parse - {}".format(footer))

        return (date, its_id)

    raise ValueError("Badly formed footer - {}".format(footer))
