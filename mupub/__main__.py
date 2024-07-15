"""The main console script entry point.

"""

import sys
from mupub.cli import dispatch


def main():
    """Dispatch with system arguments.

    This private module defines the main entry point for the command
    script. Its function is to call :py:func:`dispatch()
    <mupub.cli.dispatch>` to redirect processing to the appropriate
    command.

    More information is available in the :doc:`users-guide`.

    """

    return dispatch(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
