import os
import argparse
import functools
import getpass

def get_userpass_value(cli_value, config, key, prompt_strategy=None):
    """Gets the username / password from config.

    Uses the following rules:

    1. If it is specified on the cli (`cli_value`), use that.
    2. If `config[key]` is specified, use that.
    3. If `prompt_strategy`, prompt using `prompt_strategy`.
    4. Otherwise return None

    :param cli_value: The value supplied from the command line or `None`.
    :type cli_value: unicode or `None`
    :param config: Config dictionary
    :type config: dict
    :param key: Key to find the config value.
    :type key: unicode
    :prompt_strategy: Argumentless function to return fallback value.
    :type prompt_strategy: function
    :returns: The value for the username / password
    :rtype: unicode
    """
    if cli_value is not None:
        return cli_value
    elif config.get(key):
        return config[key]
    elif prompt_strategy:
        return prompt_strategy()
    else:
        return None


def password_prompt(prompt_text):  # Always expects unicode for our own sanity
    prompt = prompt_text
    # Workaround for https://github.com/pypa/twine/issues/116
    if os.name == 'nt' and sys.version_info < (3, 0):
        prompt = prompt_text.encode('utf8')
    return functools.partial(getpass.getpass, prompt=prompt)


get_username = functools.partial(
    get_userpass_value,
    key='username',
    prompt_strategy=functools.partial(input, 'Enter your username: '),
)
get_password = functools.partial(
    get_userpass_value,
    key='password',
    prompt_strategy=password_prompt('Enter your password: '),
)
get_cacert = functools.partial(
    get_userpass_value,
    key='ca_cert',
)
get_clientcert = functools.partial(
    get_userpass_value,
    key='client_cert',
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
