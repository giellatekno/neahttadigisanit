from flask import current_app, request
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
def define_app_short_name():
    return dict(app_short_name=current_app.config.short_name)

@blueprint.context_processor
def define_app_mobile_bookmark_name():
    return dict(app_mobile_bookmark_name=current_app.config.app_mobile_bookmark_name)

@blueprint.context_processor
def define_app_meta_keywords():
    return dict(app_meta_keywords=current_app.config.meta_keywords)

@blueprint.context_processor
def define_app_production_mode():
    return dict(production_mode=current_app.production)

@blueprint.context_processor
def define_global_language_pairs():
	return dict(language_pairs=current_app.config.pair_definitions)

@blueprint.context_processor
def define_variant_dictionaries():
	return dict(variant_dictionaries=current_app.config.variant_dictionaries)

@blueprint.context_processor
def detect_mobile_variables():
    # mobile test for most common browsers
    mobile = False
    if request.user_agent.platform in ['iphone', 'android']:
        mobile = True

    iphone = False
    if request.user_agent.platform == 'iphone':
        iphone = True

    return dict(mobile=mobile, iphone=iphone)
