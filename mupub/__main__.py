"""
The main console script entry point.

"""

import sys
from mupub.cli import dispatch
from mupub.config import config_dict

def main():
    """Dispatch with system arguments. """
    return dispatch(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
