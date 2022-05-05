from __future__ import absolute_import
from flask import current_app


def iso_filter(_iso):
    """ These things are sort of a temporary fix for some of the
    localization that runs off of CSS selectors, in order to include the
    3 digit ISO into the <body /> @lang attribute.
    """
    return current_app.config.ISO_TRANSFORMS.get(_iso, _iso)


def get_locale():
    """ Always return the three character locales
    """
    from flask_babel import get_locale as get_

    locale = iso_filter(unicode(get_()))

    return locale
