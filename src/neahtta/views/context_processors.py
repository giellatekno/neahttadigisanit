from flask import current_app
from . import blueprint

@blueprint.context_processor
def add_languages():
    """ Add internationalization languages to global context for
    templates.
    """
    return dict(internationalizations=current_app.config.locales_available)

@blueprint.context_processor
def define_app_name():
    """ Add the custom current_app name from configs to global context for
    templates.
    """
    return dict(app_name=current_app.config.app_name)

@blueprint.context_processor
def define_app_meta():
    return dict(app_meta_desc=current_app.config.meta_description)

@blueprint.context_processor
def define_app_title():
    return dict(app_meta_title=current_app.config.app_meta_title)

@blueprint.context_processor
def define_app_meta_keywords():
    return dict(app_meta_keywords=current_app.config.meta_keywords)

