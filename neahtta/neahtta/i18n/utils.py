import os
import inspect

import babel
from babel.core import UnknownLocaleError
from flask import current_app


def iso_filter(_iso):
    """These things are sort of a temporary fix for some of the
    localization that runs off of CSS selectors, in order to include the
    3 digit ISO into the <body /> @lang attribute.
    """
    return current_app.config.ISO_TRANSFORMS.get(_iso, _iso)


def copy_custom_locales():
    """If the custom locale data was not copied into babel before starting up,
    do it here"""
    babel_dir = os.path.dirname(inspect.getfile(babel))
    babel_locale_data_dir = babel_dir + "/locale-data/"

    current_dir = os.path.dirname(os.path.realpath(__file__))
    custom_locale_data_files = current_dir + "/../locale-data/*"

    os.system(f"cp {custom_locale_data_files} {babel_locale_data_dir}")


def get_locale():
    """Always return the three character locales
    The return value of flask_babel's get_locale() depends on
    the return value of application.py's get_locale()
    """
    from flask_babel import get_locale as get_

    try:
        locale = iso_filter(get_())
    except UnknownLocaleError:
        copy_custom_locales()
        locale = iso_filter(get_())

    return locale
