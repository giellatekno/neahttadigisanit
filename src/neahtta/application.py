__all__ = [
    'create_app'
]

ADMINS = [
    'ryan.txanson+nds@gmail.com',
]

import sys, os
import logging
import urllib

from   flask                          import ( Flask
                                             , request
                                             , session
                                             )

# from   werkzeug.contrib.cache         import SimpleCache
from   config                         import Config
from   logging                        import getLogger

from   flask.ext.babel                 import Babel

from cache                            import cache

# Configure user_log
user_log = getLogger("user_log")
useLogFile = logging.FileHandler('user_log.txt')
user_log.addHandler(useLogFile)
user_log.setLevel("INFO")

def jinja_options_and_filters(app):

    from filters import register_filters

    app = register_filters(app)
    app.jinja_env.line_statement_prefix = '#'
    app.jinja_env.add_extension('jinja2.ext.i18n')
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    return app

def register_babel(app):

    babel = Babel(app)
    babel.init_app(app)

    app.babel = babel

    @app.before_request
    def append_session_globals():
        """ Add two-character and three-char session locale to global
        template contexts: session_locale, session_locale_long_iso.
        """

        from i18n.utils import iso_filter
        from socket import gethostname
        from itertools import izip_longest

        loc = get_locale()

        app.jinja_env.globals['session_locale'] = loc
        app.jinja_env.globals['zip'] = zip
        app.jinja_env.globals['izip_longest'] = izip_longest
        app.jinja_env.globals['session_locale_long_iso'] = iso_filter(loc)

    @app.babel.localeselector
    def get_locale():
        """ This function defines the behavior involved in selecting a
        locale. """

        locales = app.config.locales_available

        # Does the locale exist already?
        ses_lang = session.get('locale', None)
        if ses_lang is not None:
            return ses_lang
        else:
            # Is there a default locale specified in config file?
            ses_lang = app.config.default_locale
            if not app.config.default_locale:
                # Guess the locale based on some magic that babel performs
                # on request headers.
                ses_lang = request.accept_languages.best_match(locales)
            # Append to session
            session.locale = ses_lang
            app.jinja_env.globals['session'] = session

        return ses_lang

    return app


def create_app():
    """ Set up the Flask app, cache, read app configuration file, and
    other things.
    """
    import views
    import configs

    from morpholex import MorphoLexicon

    # TODO: this is called twice sometimes, slowdowns have been reduced,
    # but don't know why yet. Need to check. It only happens on the
    # first POST lookup, however...

    # import inspect
    # curframe = inspect.currentframe()
    # calframe = inspect.getouterframes(curframe, 2)
    # print "caller name", calframe[1]

    app = Flask(__name__,
        static_url_path='/static',)

    app = jinja_options_and_filters(app)
    app.production = False
    app.register_blueprint(views.blueprint)

    app.config['cache'] = cache
    app.config['jinja_env'] = app.jinja_env

    app.config['jinja_env'] = app.jinja_env
    app.config = Config('.', defaults=app.config)
    app.config.from_envvar('NDS_CONFIG')
    app.config.overrides = configs.blueprint.load_language_overrides(app)
    app.config.prepare_lexica()

    # Register language specific config information
    app.register_blueprint(configs.blueprint)

    # Prepare cache
    cache_path = os.path.join(os.getcwd(), 'tmp/generator_cache/%s/' % app.config.short_name)
    cache.init_app(app, {'CACHE_TYPE': 'filesystem', 'CACHE_DIR': cache_path})

    app.cache = cache

    with app.app_context():
        app.cache.clear()

    app.config['cache'] = cache

    app.morpholexicon = MorphoLexicon(app.config)

    from configs.paradigms import ParadigmConfig

    pc = ParadigmConfig(app)
    app.morpholexicon.paradigms = pc

    if app.config.new_style_templates:
        from configs.entry_template_filters import register_template_filters
        app = register_template_filters(app)

        from configs.entry_templates import TemplateConfig
        pc = TemplateConfig(app, debug=True)
        app.lexicon_templates = pc
    else:
        app.lexicon_templates = False

    try:
        with open('secret_key.do.not.check.in', 'r') as F:
            key = F.readlines()[0].strip()
        app.config['SECRET_KEY'] = key
    except IOError:
        print >> sys.stderr, """
        You need to generate a secret key, and store it in a file with the
        following name: secret_key.do.not.check.in """
        sys.exit()

    app = register_babel(app)
    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler('127.0.0.1',
                                   'server-error@gtweb.uit.no',
                                   ADMINS, 'NDS error')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    
    from logging import FileHandler
    from logging.handlers import SMTPHandler
    from socket import gethostname

    if app.debug:
        mail_handler = FileHandler('debug_email_log.txt')
    else:
        _admins = ADMINS + app.config.admins
        mail_handler = SMTPHandler('127.0.0.1',
                                   "server-error@%s" % gethostname(),
                                   ADMINS, "NDS-%s Failed" %  app.config.short_name)
        app.logger.smtp_handler = mail_handler

    mail_handler.setLevel(logging.ERROR)

    app.logger.addHandler(mail_handler)

    return app
