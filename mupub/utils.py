"""Utility functions for mupub.
"""
__docformat__ = 'reStructuredText'

import os
import argparse
import ruamel.yaml as yaml
import mupub.config


class ConfigDumpAction(argparse.Action):
    """Dump the configuration to stdout.

    An argparse action to dump configuration values.

    """

    def __init__(self, option_strings, dest, **kwargs):
        super(ConfigDumpAction, self).__init__(
            option_strings,
            dest,
            **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)
        print(yaml.dump(mupub.config.config_dict,
                        Dumper=yaml.RoundTripDumper)
        )


class EnvDefault(argparse.Action):
    """Get values from environment variable.

    A custom argparse action that checks the environment for the value
    of an argument in the parser.

    """
    def __init__(self, env, required=True, default=None, **kwargs):
        default = os.environ.get(env, default)
        self.env = env
        if default:
            required = False
        super(EnvDefault, self).__init__(
            default=default,
            required=required,
            **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
