import logging
import os
import sys
from logging import getLogger
from time import perf_counter_ns

from flask import Flask, request, session
from flask_babel import Babel

from neahtta.config import Config
from neahtta.utils.chdir import working_directory

from webassets.filter import Filter, register_filter

__all__ = ["create_app"]

ADMINS = ["anders.lorentsen@uit.no"]

# Configure user_log
user_log = getLogger("user_log")
useLogFile = logging.FileHandler("user_log.txt")
user_log.addHandler(useLogFile)
user_log.setLevel("INFO")


def cwd(x):
    return os.path.join(os.path.dirname(__file__), x)


def jinja_options_and_filters(app):
    from neahtta.filters import register_filters

    app = register_filters(app)
    app.jinja_env.line_statement_prefix = "#"
    app.jinja_env.add_extension("jinja2.ext.i18n")
    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.add_extension("jinja2.ext.loopcontrols")

    return app


def register_babel(app):
    def get_locale():
        if existing := session.get("force_locale"):
            return existing
        if existing := session.get("locale"):
            return existing

        locale = app.config.default_locale
        if not locale:
            locale = request.accept_languages.best_match(app.config.locales_available)
        session.locale = locale
        app.jinja_env.globals["session"] = session
        return locale

    babel = Babel(app)
    babel.init_app(app, locale_selector=get_locale)

    app.babel = babel

    @app.before_request
    def append_session_globals():
        """Add two-character and three-char session locale to global
        template contexts: session_locale, session_locale_long_iso.
        """
        from itertools import zip_longest
        from neahtta.i18n.utils import iso_filter

        loc = get_locale()

        app.jinja_env.globals["session_locale"] = loc
        app.jinja_env.globals["zip"] = zip
        app.jinja_env.globals["izip_longest"] = zip_longest
        app.jinja_env.globals["session_locale_long_iso"] = iso_filter(loc)

    return app


def prepare_assets(app):
    """Prepare asset registries, collect and combine them into several lists.

    Prepare template tags for collecting additional assets along the way.
    """
    # TODO: how to collect additional assets called in templates?

    from socket import gethostname
    from flask_assets import Environment

    js_dev_assets = []
    css_dev_assets = []

    if gethostname() != "gtdict.uit.no":
        print("Including dev assets...")
        js_dev_assets = ["js/test_palette.js"]
        css_dev_assets = ["css/test_palette.css"]

    assets = Environment(app)

    # anders: since we're using just 1 index.js file which imports all
    # other files, and using esbuild to bundle it, that index file never
    # changes, and so, flask never picks up any changes to our bundle.
    # We explicitly tell webassets to instead of looking at the contents
    # of that one file, to look at the last modified time. So now, we
    # can `touch` the index file when we have js updates.
    assets.versions = "timestamp"

    # don't add the query param
    assets.url_expire = False
    app.assets = assets

    # assumes you've npm install uglify
    # anders: path change
    # if not os.path.exists("./neahtta/node_modules/uglify-js/bin/uglifyjs"):
    #    sys.exit("Couldn't find uglify js: `npm install uglify-js`")

    # app.assets.config["UGLIFYJS_BIN"] = "./neahtta/node_modules/uglify-js/bin/uglifyjs"
    app.assets.init_app(app)

    proj_css = []
    if app.config.has_project_css:
        proj_css.append(app.config.has_project_css.replace("static/", ""))

    app.assets.main_js_assets = [
        "js/DSt.js",
        "js/bootstrap-collapse.js",
        "js/bootstrap-dropdown.js",
        "js/bootstrap-tooltip.js",
        "js/standalone-app.js",
        "js/autocomplete.js",
        # "js/bootstrap-typeahead-fork.js",
        # "js/base.js",
        # "js/index.js",
        # "js/detail.js",
        # TODO: underscore? angular? async_paradigms?
    ] + js_dev_assets

    app.assets.main_css_assets = (
        [
            "css/bootstrap.css",
            "css/bootstrap-responsive.css",
            "css/base.css",
            "css/detail.css",
            "css/about.css",
        ]
        + proj_css
        + css_dev_assets
    )

    app.assets.t_css_assets = [
        "bootstra.386/css/bootstrap.css",
        "bootstra.386/css/bootstrap-responsive.css",
        "css/text-tv-base.css",
    ] + proj_css

    app.assets.t_js_assets = [
        "bootstra.386/js/jquery.js",
        "bootstra.386/js/bootstrap-386.js",
    ]

    # mobile nav
    app.assets.nav_menu_css = [
        "navmenu/css/normalize.css",
        "navmenu/css/icons.css",
        "navmenu/css/component.css",
    ]

    # for footer
    app.assets.nav_menu_js = [
        "navmenu/js/modernizr.custom.js",
        "navmenu/js/classie.js",
        "navmenu/js/mlpushmenu.js",
        "navmenu/js/mobile_nav_init.js",
    ]

    app.assets.prepared = False


class ESBuildFilter(Filter):
    "Minify and bundle Javascript using esbuild."

    name = "esbuild"

    # def input(self, _in, out, source_path=None, **kwargs):
    # docs are confusing and/or wrong:
    # this DOES get called one for each file that is changed, BUT
    # no concatenation seems to take place. So instead, we bundle it
    # all with esbuild instead, compiling the "index_new.js" (index.js
    # already existed), which imports all files we need
    # from neahtta.utils.chdir import working_directory
    # from pathlib import Path
    # cwd = Path(source_path).parent

    #    pass

    def output(self, _in, out, **kwargs):
        import subprocess

        cmd = [
            "npm",
            "exec",
            "--",
            "esbuild",
            "--bundle",
            "--format=iife",
            "--target=es5",
            # "index_new.js",
            # "--outfile",
        ]
        with working_directory("neahtta/static/js"):
            proc = subprocess.run(
                cmd,
                # cwd=cwd,
                text=True,
                input=_in.read(),
                capture_output=True,
            )
            if proc.stderr:
                print(proc.stderr, file=sys.stderr)
            print("BUILT JS!")
        out.write(proc.stdout)


register_filter(ESBuildFilter)


def register_assets(app):
    """After all assets have been collected from parsed templates...

    * js/app-compiled-PROJNAME.js
    * js/app-t-compiled-PROJNAME.js
    * js/nav-menu-compiled-PROJNAME.js

    * css/app-compiled-PROJNAME.css
    * css/app-t-compiled-PROJNAME.css
    * css/nav-menu-compiled-PROJNAME.css

    """
    from flask_assets import Bundle

    # js_filters = "uglifyjs"
    css_filters = "cssmin"

    PROJ = app.config.short_name

    main_js = Bundle(
        "js/index_new.js",
        # *app.assets.main_js_assets,
        filters="esbuild",
        output=f"js/app-compiled-{PROJ}.js",
        depends=app.assets.main_js_assets,
    )
    print("application.py::register_assets(): bundled main_js")
    app.assets.register("main_js", main_js)

    main_css = Bundle(
        *app.assets.main_css_assets,
        filters=css_filters,
        output=f"css/app-compiled-{PROJ}.css",
    )
    app.assets.register("main_css", main_css)

    main_t_js = Bundle(
        *app.assets.t_js_assets,
        # filters=js_filters,
        output=f"js/app-t-compiled-{PROJ}.js",
    )
    app.assets.register("main_t_js", main_t_js)

    main_t_css = Bundle(
        *app.assets.t_css_assets,
        filters=css_filters,
        output=f"css/app-t-compiled-{PROJ}.css",
    )
    app.assets.register("main_t_css", main_t_css)

    nav_menu_js = Bundle(
        *app.assets.nav_menu_js,
        # filters=js_filters,
        output=f"js/nav-menu-compiled-{PROJ}.js",
    )
    app.assets.register("nav_menu_js", nav_menu_js)

    nav_menu_css = Bundle(
        *app.assets.nav_menu_css,
        filters=css_filters,
        output=f"css/nav-menu-compiled-{PROJ}.css",
    )
    app.assets.register("nav_menu_css", nav_menu_css)

    # Trigger this to prevent stuff from being reregistered on each view
    app.assets.prepared = True

    return app


def check_js_dependencies():
    from shutil import which

    if not which("node"):
        print(os.environ["PATH"], file=sys.stderr)
        sys.exit("nodejs not found in PATH, aborting (`which node`)")

    node_bin_path = os.path.join(os.path.dirname(__file__), "node_modules", ".bin")

    esbuild_path = os.path.join(node_bin_path, "esbuild")
    if not os.path.exists(esbuild_path):
        print("javascript dependencies not installed")
        print("running: npm install")
        # TODO check if succesful or not (and if it works at all, or not)
        os.system("npm install")


def create_app():
    """Create the Flask app, cache, read configs, templates and such."""
    # Updated: anders: explanation for why this function being called twice:
    # https://stackoverflow.com/questions/25504149/why-does-running-the-flask-dev-server-run-itself-twice

    import neahtta.conf as configs
    from neahtta.morpholex import MorphoLexicon
    import neahtta.views as views
    from neahtta.paradigms import ParadigmConfig
    from neahtta.entry_template_filters import register_template_filters
    from neahtta.entry_templates import TemplateConfig

    t0 = perf_counter_ns()

    check_js_dependencies()
    print("DEBUG startup:check_js_dependencies", ms_since(t0))

    app = Flask(__name__, static_url_path="/static", template_folder=cwd("templates"))
    print("DEBUG startup:Flask", ms_since(t0))

    app = jinja_options_and_filters(app)
    print("DEBUG startup:jinja_options_and_filters", ms_since(t0))
    app.production = False

    app.config = Config(".", defaults=app.config)
    print("DEBUG startup:Config", ms_since(t0))
    app.config.from_envvar("NDS_CONFIG")
    print("DEBUG startup:config.from_envvar", ms_since(t0))
    app.config.overrides = configs.blueprint.load_language_overrides(app)
    print("DEBUG startup:load_language_overrides", ms_since(t0))

    # PERF: This is a big one (~1.7 seconds)
    app.config.prepare_lexica()
    print("DEBUG startup:prepare_lexica", ms_since(t0))

    app.config.add_optional_routes()
    print("DEBUG startup:add_optional_routes", ms_since(t0))
    app.config["jinja_env"] = app.jinja_env

    setup_cache(app)
    print("DEBUG startup:setup_cache", ms_since(t0))

    # anders: we don't use fcgi anymore, is this still relevant?
    os.environ["NDS_PATH_PREFIX"] = app.config.fcgi_script_path
    app.static_url_path = app.config.fcgi_script_path + app.static_url_path

    # Prepare assets before custom templates are read
    prepare_assets(app)
    print("DEBUG startup:prepare_assets", ms_since(t0))

    register_rate_limiter(app)
    print("DEBUG startup:register_rate_limiter", ms_since(t0))

    # anders: we don't use fcgi anymore, is this still relevant?
    app.config["APPLICATION_ROOT"] = app.config.fcgi_script_path

    # Register language specific config information
    app.register_blueprint(views.blueprint, url_prefix=app.config["APPLICATION_ROOT"])
    app.register_blueprint(configs.blueprint, url_prefix=app.config["APPLICATION_ROOT"])
    print("DEBUG startup:register_blueprint (x2)", ms_since(t0))

    # Set session cookie path to root, so it can be accessed from all paths
    app.config["SESSION_COOKIE_PATH"] = "/"

    # PERF: ~350 ms
    app.morpholexicon = MorphoLexicon(app.config)
    print("DEBUG startup:MorphoLexicon", ms_since(t0))

    app.morpholexicon.paradigms = ParadigmConfig(app)
    print("DEBUG startup:ParadigmConfig", ms_since(t0))

    register_template_filters(app)
    print("DEBUG startup:register_template_filters", ms_since(t0))

    # PERF: ~1.4 seconds
    app.lexicon_templates = TemplateConfig(app, debug=True)
    print("DEBUG startup:TemplateConfig", ms_since(t0))

    app.config["SECRET_KEY"] = read_secret_key()
    print("DEBUG startup:read_secret_key", ms_since(t0))
    app = register_babel(app)
    print("DEBUG startup:register_babel", ms_since(t0))
    register_assets(app)
    print("DEBUG startup:register_assets", ms_since(t0))

    print("DEBUG startup complete", ms_since(t0))

    if os.environ.get("NDS_TRACE") == "1":
        print("NDS_TRACE env var set, starting tracing")
        from neahtta.utils.debug import tracefn

        # from sys import settrace
        from threading import settrace

        settrace(tracefn)

    return app


def register_rate_limiter(app):
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(get_remote_address, app=app, default_limits=["120/minute"])
    app.limiter = limiter


def read_secret_key():
    try:
        with open("secret_key.do.not.check.in", "r") as f:
            return f.read()
    except FileNotFoundError:
        from secrets import token_hex

        secret_key = token_hex(24)

        try:
            with open("secret_key.do.not.check.in", "w") as f:
                f.write(secret_key)
        except (PermissionError, IOError):
            sys.exit(
                "Keyfile secret_key.do.not.check.in did not exist, but "
                "could not be written to either. Make sure you have "
                "write access to the folder"
            )
        else:
            return secret_key
    except (PermissionError, IOError):
        sys.exit(
            "Keyfile secret_key.do.not.check.in could not be read. Make sure "
            "it is readable."
        )


def setup_cache(app):
    from flask_caching import Cache

    cache_dir = os.path.join(
        os.path.dirname(__file__), f"tmp/generator_cache/{app.config.short_name}/"
    )
    cache = Cache(
        config={
            "CACHE_TYPE": "FileSystemCache",
            "CACHE_DIR": cache_dir,
        }
    )
    print("DEBUG", type(cache))

    cache_options = {
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DIR": os.path.join(
            os.path.dirname(__file__), f"tmp/generator_cache/{app.config.short_name}/"
        ),
    }
    cache.init_app(app, cache_options)

    app.cache = cache
    app.config["cache"] = cache

    with app.app_context():
        app.cache.clear()


def ms_since(other):
    return (perf_counter_ns() - other) / 1_000_000
