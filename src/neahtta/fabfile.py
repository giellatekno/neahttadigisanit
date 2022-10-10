""" Tools for compiling dictionaries automatically.

Fabric will automatically execute sets of commands remotely, and will
log in via SSH automatically to do this, assuming you have the proper
credentials.

To install Fabric, follow the instructions on the website:

    http://fabfile.org/

Then run the following to check that it works.

    fab --list

## Basic commands

In order to perform a task for a specific instance, you must specify a
few things.

    fab LOCATION DICT TASKS

So, to compile the lexicon locally for baakoeh, you would run:

    $ fab (local) baakoeh compile-dictionary

To do the same remotely, and restart the service, you would run:

    $ fab gtdict sanat compile-dictionary restart-service

With the latter, Fabric will connect via SSH and run commands remotely.
You may be asked for your SSH password.

After updating to Fabric 2, not all remote commands have been debugged well.
Local Invoke execution should work.

"""

#    TODO: fab local start_project PROJNAME
#      - create infrastructure for new project
#        - configs/sample.config.yaml.in -> configs/PROJNAME.config.yaml.in
#        - templates/about.blank.html -> configs/about.PROJNAME.html
#        - grey box search notice template
#        - mkdir:
#
#    TODO: fab local add_language PROJNAME LANGISO
#      - create basic files for languages
#        - mkdir:
#            configs/language_specific_rules/tagsets/

from __future__ import absolute_import
from __future__ import print_function
import os
import socket
import sys

from config import yaml
from configtesters import chk_fst_paths
from invocations.console import confirm
from termcolor import colored

# Fabric 2
from fabric import task
from fabric.config import Config
from invoke import Exit
# Note: underscores in task names are converted to hyphens for commandline invokation, e.g. "fab sanit restart-service"

# Hosts that have an nds- init.d script
running_service = [
    'gtdict.uit.no'
]

no_fst_install = [
    'gtdict.uit.no',
]

location_restriction_notice = {
    'gtdict.uit.no': [
        'sanit', 'baakoeh', 'kyv', 'muter', 'saan', 'saanih', 'sanat',
        'sonad', 'vada', 'valks', 'bahkogirrje', 'sanj'
    ]
}

config = Config()

config.no_svn_up = False
config.load_ssh_configs = True
# config.connect_kwargs.key_filename = '~/.ssh/neahtta'


config.real_hostname = socket.gethostname()


def get_projects():
    """ Find all existing projects which can be included as an env
    argument """
    import os

    conf_suffix = ".config.yaml.in"

    avail_projects = []
    for d, ds, fs in os.walk('.'):
        for f in fs:
            if f.endswith(conf_suffix):
                avail_projects.append(f.replace(conf_suffix, ''))

    return avail_projects


def get_project():
    avail_projects = get_projects()

    proj_arg = [a for a in sys.argv if a in avail_projects]

    if len(proj_arg) > 0:
        proj_arg = proj_arg[0]
    else:
        proj_arg = False

    return proj_arg


@task(aliases=get_projects())
def set_proj(ctx):
    """ Set the project. This is aliased to whatever existing project
    names there are. ... Assuming no project name will be 'local' or
    'compile' """
    proj = get_project()

    config.clean_first = False

    if proj:
        config.current_dict = proj
    else:
        print("This is not a valid project name.", file=sys.stderr)
        sys.exit()

    host = socket.gethostname()

    if host in running_service:
        has_restriction = sum(location_restriction_notice.values(), [])
        if proj in has_restriction:
            host_rest = location_restriction_notice.get(host, False)
            if host_rest:
                if proj not in host_rest:
                    print(colored(
                        "%s is not on the current host <%s>." % (proj, host), "red"), file=sys.stderr)
                    cont = raw_input(colored('Continue anyway? [Y/N] \n', "red"))
                    if cont != 'Y':
                        sys.exit()

    return


@task
def local(ctx):
    config_local()

def config_local(*args, **kwargs):
    """ Run a command using the local environment.
    """
    import os

    config.host = "localhost"
    config.user = None

    gthome = os.environ.get('GTHOME')

    if gthome is None:
        sys.exit("GTHOME environment variable is not set.")

    config.path_base = os.getcwd()

    config.svn_path = gthome
    config.dict_path = os.path.join(config.path_base, 'dicts')
    config.neahtta_path = config.path_base
    config.i18n_path = os.path.join(config.path_base, 'translations')

    # Make command needs to include explicit path to file, because of
    # fabric.
    config.make_cmd = "make -C %s -f %s" % (
        config.dict_path, os.path.join(config.dict_path, 'Makefile'))
    config.remote_no_fst = False

if ['local', 'gtdict'] not in sys.argv:
    config_local()

# set up environments
# Assume local unless otherwise noted


@task
def no_svn_up(ctx):
    """ Do not SVN up """
    config.no_svn_up = True

@task
def gtdict(ctx):
    """ Run a command remotely on gtdict
    """
    config.host = "gtdict.uit.no"
    config.user = "neahtta"
    config.path_base = '/home/neahtta'

    config.svn_path = config.path_base + '/gtsvn'
    config.dict_path = config.path_base + '/neahtta/dicts'
    config.neahtta_path = config.path_base + '/neahtta'
    config.i18n_path = config.path_base + '/neahtta/translations'

    config.make_cmd = "make -C %s -f %s" % (
        config.dict_path, os.path.join(config.dict_path, 'Makefile'))
    config.remote_no_fst = True


@task
def update_repo(ctx):
    """ Pull repository to update files """
    if config.no_svn_up:
        print((colored("** skipping git pull **", "yellow")))
        return

    with ctx.cd(config.neahtta_path):
        print((colored("** git pull **", "cyan")))
        ctx.run("git pull")


def read_config(proj):

    import yaml

    def gettext_yaml_wrapper(loader, node):
        from flask_babel import lazy_gettext as _
        return node.value

    yaml.add_constructor('!gettext', gettext_yaml_wrapper)

    _path = 'configs/%s.config.yaml' % proj

    try:
        open(_path, 'r').read()
    except IOError:
        if config.real_hostname not in running_service:
            _path = 'configs/%s.config.yaml.in' % proj
            print((
                colored(
                    "** Production config not found, using development (*.in)", "yellow")
            ))
        else:
            print((
                colored("** Production config not found, and on a production server. Exiting.", "red"
                    )))
            sys.exit()

    with open(_path, 'r') as F:
        config_file = yaml.load(F)

    return config_file


@task
def update_gtsvn(ctx):
    """ SVN up the various ~/gtsvn/ directories """

    if config.no_svn_up:
        print((colored("** skipping svn up **", "yellow")))
        return

    with ctx.cd(config.svn_path):
        config_file = read_config(config.current_dict)
        svn_langs = [
            l.get('iso') for l in config_file.get('Languages')
            if not l.get('variant', False)
        ]
        # TODO: replace langs with specific list of langs from config
        # file
        paths = [
            'words/'
        ] 
        print((colored("** svn up **", "cyan")))
        for p in paths:
            _p = os.path.join(config.svn_path, p)
            try:
                svn_up_cmd = ctx.run('svn up {}'.format(_p))
            except:
                raise Exit(
                    colored("\n* svn up failed in <%s>. Prehaps the tree is locked?" % _p, "red") + '\n' + \
                    colored("  Correct this (maybe with `svn cleanup`) and rerun the command, or run with `no_svn_up`.", "red")
                )
    return

    # TODO: necessary to run autogen just in case?
    # no need to compile giella-core
    '''
    print(colored("** Compiling giella-core **", "cyan"))
    giella_core = os.path.join(config.svn_path , 'giella-core')
    with cd(giella_core):
        make_file = config.svn_path + '/giella-core/Makefile'
        make_ = "make -C %s -f %s" % ( giella_core
                                     , make_file
                                     )
        result = config.run(make_)
    '''


@task
def restart_service(ctx, dictionary=False):
    """ Restarts the service. """

    if not dictionary:
        try:
            dictionary = config.current_dict
        except AttributeError:
            print(colored("Error: Remember to specify a project", "red"))
            sys.exit()

    fail = False

    # Not a big issue, but figure this out for local development.
    # if config.real_hostname not in running_service:
    #     print config.real_hostname
    #     print(colored("** No need to restart, nds-<%s> not available on this host. **" % dictionary, "green"))
    #     return

    with ctx.cd(config.neahtta_path):
        _path = '%s.wsgi' % config.current_dict
        try:
            os.utime(_path, None)
            touched = True
        except Exception as e:
            touched = False
        if touched:
            print((colored("** Restarting service for <%s> **" % dictionary, "cyan")))
            sys.exit()

        print((colored("** Restarting service for <%s> **" % dictionary, "cyan")))
        restart = ctx.run("sudo service nds-%s restart" % dictionary)
        if not restart.failed:
            print(colored("** <%s> Service has restarted successfully **" % dictionary, "green"))
        else:
            fail = True

    if fail:
        print(
            colored("** something went wrong while restarting <%s> **" %
                dictionary, "red"))


@task
def compile_dictionary(ctx, dictionary=False, restart=False):
    """ Compile a dictionary project on the server, and restart the
    corresponding service.

        $ fab compile-dictionary [-d DICT]
    """

    failed = False

    if not dictionary:
        try:
            dictionary = config.current_dict
        except AttributeError:
            print(colored("Error: Remember to specify a project", "red"))
            sys.exit()

    update_gtsvn(ctx)

    with ctx.cd(config.dict_path):
        ctx.run("git pull")

        result = ctx.run(config.make_cmd + " %s-lexica" % dictionary)

        if result.failed:
            failed = True

    if restart:
        restart_service(ctx, dictionary)

    if failed:
        print((
            colored("** Something went wrong while compiling <%s> **" %
                dictionary), "red"))


@task
def compile(ctx, dictionary=False, restart=False):
    """ Compile a dictionary, fsts and lexica, on the server.

        $ fab compile [-d DICT]

        NB: if the hostname is gtdict.uit.no (set in no_fst_install
        list above), only the lexicon will be compiled, FSTs will not be
        compiled or installed.
    """

    hup = False
    failed = False

    print((colored("Executing on <%s>" % config.real_hostname, "cyan")))

    if not dictionary:
        try:
            dictionary = config.current_dict
        except AttributeError:
            print(colored("Error: Remember to specify a project", "red"))
            sys.exit()

    update_repo(ctx)
    update_gtsvn(ctx)

    with ctx.cd(config.dict_path):
        if config.no_svn_up:
            print((colored("** Skipping git pull of Makefile", "yellow")))
        else:
            ctx.run("git pull")

        if config.real_hostname in no_fst_install or config.remote_no_fst:
            print((colored("** Skip FST compile for gtdict **", "yellow")))
            print((colored("** Compiling lexicon for <%s> **" % dictionary, "cyan")))
            result = ctx.run(config.make_cmd + " %s-lexica" % dictionary)
            skip_fst = True
        else:
            skip_fst = False

            print((
                colored("** Compiling lexicon and FSTs for <%s> **" % dictionary, "cyan")))

            if config.clean_first in ['Y', 'y']:
                clean_result = ctx.run(config.make_cmd + " %s-clean" % dictionary)

            result = ctx.run(config.make_cmd + " %s" % dictionary)

        if not skip_fst and not result.succeeded:
            print((
                colored("** There was some problem building the FSTs for this dictionary.",
                    "red")))
            print((
                colored("** Remove and check out individual language directories first?",
                    "red")))
            print((
                colored("** WARNING: this will run `rm -rf $GTHOME/giellalt/LANG-XXX for each",
                    "red")))
            print((
                colored("**          language in the current project. If you have", "red")
            ))
            print((colored("**          local changes, they will be lost.", "red")))
            if confirm('Do you want to continue?'):
                compile(ctx, dictionary, restart)
            failed = True
                

        if not skip_fst:
            print((colored("** Installing FSTs for <%s> **" % dictionary, "cyan")))
            result = ctx.run(config.make_cmd + " %s-install" % dictionary)
            if result.failed:
                failed = True

    if restart:
        restart_service(ctx, dictionary)

    if failed:
        print((
            colored("** Something went wrong while compiling <%s> **" %
                dictionary, "red")))
    else:
        print((
            colored(
                "** <%s> FSTs and Lexicon compiled okay, should be safe to restart. **"
                % dictionary, "cyan")))


@task
def compile_fst(ctx, iso='x'):
    """ Compile a dictionary project on the server.

        $ fab compile_dictionary [-i ISO]
    """

    hup = False

    try:
        dictionary = config.current_dict
    except AttributeError:
        print(colored("Error: Remember to specify a project", "red"))
        sys.exit()

    update_gtsvn(ctx)

    # TODO: need a make path to clean existing dictionary
    with ctx.cd(config.dict_path):
        # ctx.run("svn up Makefile")
        print((colored("** Compiling FST for <%s> **" % iso, "cyan")))

        clear_tmp = ctx.run(config.make_cmd + " rm-%s" % iso)

        make_fsts = ctx.run(config.make_cmd + " %s" % iso)
        make_fsts = ctx.run(config.make_cmd +
                            " %s-%s-install" % (dictionary, iso))

        if make_fsts.failed:
            print((colored("** Something went wrong while compiling <%s> **" % iso, "red")))
        else:
            print((colored("** FST <%s> compiled **" % iso, "cyan")))

@task
def test_configuration(ctx):
    """ Test the configuration and check language files for errors. """

    try:
        _path = 'configs/%s.config.yaml' % config.current_dict
    except AttributeError:
        print(colored("Error: Remember to specify a project", "red"))
        sys.exit()

    try:
        open(_path, 'r').read()
    except IOError:
        if config.real_hostname not in running_service:
            _path = 'configs/%s.config.yaml.in' % config.current_dict
            print((
                colored(
                    "** Production config not found, using development (*.in)", "yellow")
            ))
        else:
            print((
                colored("** Production config not found, and on a production server. Exiting.",
                    "yellow")))
            sys.exit()

    # TODO: this assumes virtualenv is enabled, need to explicitly enable
    _dict = config.current_dict
    with ctx.cd(config.neahtta_path):
        print((colored("** Checking paths and testing XML for <%s> **" % _dict, "cyan")))

        os.environ['NDS_CONFIG'] = _path
        chk_fst_paths()


@task
def extract_strings(ctx):
    """ Extract all the translation strings to the template and *.po files. """

    print((colored("** Extracting strings", "cyan")))
    cmd = "pybabel extract -F babel.cfg -k gettext -o translations/messages.pot ."
    extract_cmd = ctx.run(cmd)
    if extract_cmd.failed:
        print((colored("** Extraction failed, aborting.", "red")))
    else:
        print((colored("** Extraction worked, updating files.", "cyan")))
        cmd = "pybabel update -i translations/messages.pot -d translations"
        update_cmd = ctx.run(cmd)
        if update_cmd.failed:
            print((colored("** Update failed.", "red")))
        else:
            print((
                colored("** Update worked. You may now check in or translate.", "green")))


@task
def update_strings(ctx):
    """Must pull entire repo as we have moved to git"""
    update_repo(ctx)

    compile_strings(ctx)


@task
def find_babel(ctx):
    import babel
    print (babel)


# TODO: handle babel.core.UnknownLocaleError: unknown locale 'hdn', with
# cleaner error message
@task
def compile_strings(ctx):
    """ Compile .po strings to .mo strings for use in the live server. """

    if hasattr(config, 'current_dict'):
        try:
            config_file = 'configs/%s.config.yaml.in' % config.current_dict
        except AttributeError:
            print(colored("Error: Remember to specify a project", "red"))
            sys.exit()
        with open(config_file, 'r') as F:
            _y = yaml.load(F.read())
            langs = _y.get('ApplicationSettings', {}).get('locales_available')

        for lang in langs:
            # run for each language
            cmd = "pybabel compile -d translations -l %s" % lang
            compile_cmd = ctx.run(cmd)
            if compile_cmd.failed:
                print((colored("** Compilation failed, aborting.", "red")))
            else:
                print((colored("** Compilation successful.", "green")))
    else:
        cmd = "pybabel compile -d translations"
        compile_cmd = ctx.run(cmd) # previously warn only and capture, probably not needed now
        if compile_cmd.failed:
            if 'babel.core.UnknownLocaleError' in compile_cmd.stderr:
                error_line = [
                    l for l in compile_cmd.stderr.splitlines()
                    if 'babel.core.UnknownLocaleError' in l
                ]
                print((
                    colored("** String compilation failed, aborting:  ", "red") + colored(
                        ''.join(error_line), "cyan")))
                print("")
                print((colored("  Either: ", "yellow")))
                print((
                    colored(
                        "   * rerun the command with the project name, i.e., `fab PROJNAME compile_strings`.",
                        "yellow"
                    )))
                print((
                    colored(
                        "   * Troubleshoot missing locale. (see Troubleshooting doc)",
                        "yellow"
                    )))
            else:
                print((compile_cmd.stderr))
                print((colored("** Compilation failed, aborting.", "red")))
        else:
            print((compile_cmd.stdout))
            print((colored("** Compilation successful.", "green")))


def where(iso):
    """ Searches Config and Config.in files for languages defined in
    Languages. Returns list of tuples.

        (config_path, short_name, iso)

    """

    configs = []
    for d, path, fs in os.walk('configs/'):
        for f in fs:
            if f.endswith(('.config.yaml.in', '.config.yaml')):
                configs.append(os.path.join(d, f))

    def test_lang(i):
        if isinstance(iso, list):
            if i.get('iso') in iso:
                return True
        else:
            if i.get('iso') == iso:
                return True
        return False

    locations = []
    for config_file in configs:
        with open(config_file, 'r') as F:
            _y = yaml.load(F.read())
            short_name = _y.get('ApplicationSettings', {}).get('short_name')
            langs = filter(test_lang, _y.get('Languages'))

            for l in langs:
                locations.append((config_file, short_name, l.get('iso')))

    return locations


@task
def where_is(ctx, iso='x'):
    """ Search *.in files for language ISOs to return projects that the
    language is present in. Use parameter --iso=<iso code>"""

    if '+' in iso:
        iso = iso.split('+')

    locations = where(iso)

    for config_file, shortname, l in locations:
        print(('%s : %s\t\t%s' % (l, shortname, config_file)))


def search_running():
    """ Find all running services, return tuple of shortname and pidfile path
    """
    pidfile_suffix = "-pidfile.pid"

    pids = []
    for d, ds, fs in os.walk('.'):
        for f in fs:
            if f.endswith(pidfile_suffix):
                pids.append((f.replace(pidfile_suffix, ''), os.path.join(d,
                                                                         f)))

    return pids


@task
def find_running(ctx):
    hostname = config.real_hostname
    for shortname, pidfile in search_running():
        print(("%s running on %s (%s)" % (colored(shortname, "green"), colored(hostname, "yellow"),
                                         pidfile)))


@task
def restart_running(ctx):
    hostname = config.real_hostname
    find_running(ctx)

    with ctx.cd(config.neahtta_path):
        running_services = search_running()
        failures = []

        for s, pid in running_services:
            print((colored("** Restarting service for <%s> **" % s, "cyan")))
            stop = ctx.run("sudo service nds-%s stop" % s)
            if not stop.failed:
                start = ctx.run("sudo service nds-%s start" % s)
                if not start.failed:
                    print((
                        colored("** <%s> Service has restarted successfully **" %
                              s, "green")))
                else:
                    failures.append((s, pid))
            else:
                failures.append((s, pid))

    if len(failures) > 0:
        print((colored("** something went wrong while restarting the following **", "red")))
        for f in failures:
            print((s, pid))


@task
def runserver(ctx):
    """ Run the development server."""

    try:
        _path = 'configs/%s.config.yaml' % config.current_dict
    except AttributeError:
        print(colored("Error: Remember to specify a project", "red"))
        sys.exit()

    try:
        open(_path, 'r').read()
    except IOError:
        if config.real_hostname not in running_service:
            _path = 'configs/%s.config.yaml.in' % config.current_dict
            print((
                colored(
                    "** Production config not found, using development (*.in)", "yellow")
            ))
        else:
            print((
                colored("** Production config not found, and on a production server. Exiting.",
                    "red")))
            sys.exit()

    cmd = "NDS_CONFIG=%s python neahtta.py dev" % _path
    print((colored("** Go.", "green")))
    run_cmd = ctx.run(cmd)
    if run_cmd.failed:
        print((colored("** Starting failed for some reason.", "red")))


@task
def doctest(ctx):
    """ Run unit tests embedded in code
    """

    doctests = [
        'morphology/utils.py',
    ]

    doctest_cmd = 'python -m doctest -v %s'

    for _file in doctests:
        test_cmd = ctx.run(doctest_cmd % _file)


@task
def test_project(ctx):
    """ Test the configuration and check language files for errors. """

    try:
        yaml_path = 'configs/%s.config.yaml.in' % config.current_dict
    except AttributeError:
        print(colored("Error: Remember to specify a project", "red"))
        sys.exit()

    _dict = config.current_dict
    with ctx.cd(config.dict_path):
        print((colored("** Running tests for %s" % _dict, "cyan")))

        cmd = "NDS_CONFIG=%s python -m unittest tests.yaml_tests" % (yaml_path)
        test_cmd = ctx.run(cmd)

        if test_cmd.failed:
            print((colored("** Something went wrong while testing <%s> **" % _dict, "red")))


@task
def unittests(ctx):
    """ Test the configuration and check language files for errors.

        TODO: this is going away in favor of the better new thing: `test_project`, `doctest`, and `test`
    """

    try:
        yaml_path = 'tests/configs/%s.config.yaml' % config.current_dict
    except AttributeError:
        print(colored("Error: Remember to specify a project", "red"))
        sys.exit()

    try:
        with open(yaml_path, 'r') as F:
            _y = yaml.load(F)
    except IOError:
        if config.real_hostname not in running_service:
            yaml_path = 'configs/%s.config.yaml.in' % config.current_dict
            print((
                colored(
                    "** Production config not found, using development (*.in)", "yellow")
            ))
            with open(yaml_path, 'r') as F:
                _y = yaml.load(F)
        else:
            print((
                colored("** Production config not found, and on a production "
                    "server. Exiting.", "red")))
            sys.exit()

    # TODO: this assumes virtualenv is enabled, need to explicitly enable
    _dict = config.current_dict
    with ctx.cd(config.dict_path):
        unittest_modules = _y.get('UnitTests', False)
        if not unittest_modules:
            print((colored("** `UnitTests` not found in %s. Example:" % yaml_path, "red")))
            print("", file=sys.stderr)
            print("    UnitTests:", file=sys.stderr)
            print('     - "tests.LANG1_lexicon"', file=sys.stderr)
            print('     - "tests.LANG2_lexicon"', file=sys.stderr)
            print("", file=sys.stderr)
            sys.exit()

        for unittest in unittest_modules:

            # unittest_file = unittest.replace('/', '.') + '.py'
            # try:
            #     open(os.path.join(config.path_base, unittest_file.replace('/', '.') + '.py'), 'r').read()
            # except:
            #     print(colored("** File does not exist for %s" % unittest_file, "yellow"))
            #     continue

            print((colored("** Running tests for %s" % unittest, "cyan")))

            cmd = "NDS_CONFIG=%s python -m unittest %s" % (yaml_path, unittest)
            test_cmd = ctx.run(cmd)

            if test_cmd.failed:
                print((
                    colored("** Something went wrong while testing <%s> **" %
                        _dict, "red")))


@task
def test(ctx):
    doctest(ctx)
    test_project(ctx)


def commit_gtweb_tag():
    """

    svn rm nds-stable-gtweb
    svn commit nds-stable-gtweb -m "preparing for update"
    https://gtsvn.uit.no/langtech/tags/apps/dicts/nds
    svn copy https://gtsvn.uit.no/langtech/trunk/apps/dicts/nds nds-stable-gtweb
    """


def get_status_code(host, path="/"):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        None instead.
    """
    import httplib
    try:
        conn = httplib.HTTPConnection(host)
        conn.request("HEAD", path)
        return conn.getresponse().status
    except Exception:
        return None


@task
def test_running(ctx):

    hosts = [
        "sanit.oahpa.no",
        "baakoeh.oahpa.no",
        "kyv.oahpa.no",
        "saanih.oahpa.no",
        "valks.oahpa.no",
        "muter.oahpa.no",
        "saanih.oahpa.no",
        "saan.oahpa.no",
        "sonad.oahpa.no",
        "vada.oahpa.no",
        "bahkogirrje.oahpa.no",
        "sanj.oahpa.no",
        "sanat.oahpa.no"
    ]

    for h in hosts:
        code = get_status_code(h)
        if code != 200:
            col = "red"
            msg = 'ERROR? ' + str(code) + ' '
        else:
            col = "green"
            msg = ''
        print((colored(msg + h, col)))

@task
def add_stem2dict(ctx):
    """ Runs the script add_stemtype2xml.py to add stem type in sme-nob dict. 
        
        This function makes a backup of sme-nob dict.
        Runs the script add_stemtype2xml.py to add stem type in sme-nob dict.
        Overwrite the current xml with the new one with stem type.

        To make sure changes are made on the latest version of the dictionary, you have to run first
        fab sanit compile
    """
    cmd = 'cp dicts/sme-nob.all.xml dicts/sme-nob.all.xml.bak-before-stem'
    cp_cmd = ctx.run(cmd)

    if cp_cmd.failed:
        print((colored("** Backup xml failed, aborting.", "red")))
        return
    else:
        print((colored("** Backing up xml" , "cyan")))

    lexc_list = ['nouns', 'adjectives', 'verbs', 'prop']

    for lexc in lexc_list:
        if not lexc == 'prop':
            lexc_cmd = 'python $GTHOME/words/dicts/scripts/add_stemtype2xml.py ' + lexc + ' $GTHOME/words/dicts/smenob/scripts/' + lexc + '_stemtypes.txt dicts/sme-nob.all.xml $GTLANGS/lang-sme/src/fst/stems/' + lexc + '.lexc'
        else:
            lexc_cmd = 'python $GTHOME/words/dicts/scripts/add_stemtype2xml.py prop $GTHOME/words/dicts/smenob/scripts/' + lexc + '_stemtypes.txt dicts/sme-nob.all.xml $GTLANGS/lang-sme/src/fst/stems/sme-propernouns.lexc $GTLANGS/giella-shared/smi/src/fst/stems/smi-propernouns.lexc'


        add_cmd = ctx.run(lexc_cmd)

        if add_cmd.failed:
            print((colored("** Add stem type for %s to xml failed, aborting." %lexc, "red")))
            return
        else:
            print((colored("** Successfully added stem type for %s to xml"  %lexc, "green")))

        cmd = 'cp dicts/sme-nob.all.xml.stem.xml dicts/sme-nob.all.xml'
        overwrite_cmd = ctx.run(cmd)

        if overwrite_cmd.failed:
            print((colored("** Overwrite xml failed, aborting.", "red")))
            return
        else:
            print((colored("** Overwriting xml" , "cyan")))
