def iso_filter(_iso):
    """ These things are sort of a temporary fix for some of the
    localization that runs off of CSS selectors, in order to include the
    3 digit ISO into the <body /> @lang attribute.
    """
    from configs.language_names import ISO_TRANSFORMS
    return ISO_TRANSFORMS.get(_iso, _iso)

def get_locale():
    """ Always return the three character locales
    """
    from flask.ext.babel import get_locale as get_

    locale = iso_filter(unicode(get_()))

    return locale
