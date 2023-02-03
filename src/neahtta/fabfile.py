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

import os
import socket
import sys

from pathlib import Path

from invocations.console import confirm
from termcolor import colored

from fabric import task
from fabric.config import Config
from invoke import Exit

from configtesters import chk_fst_paths
from config import yaml
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

config.load_ssh_configs = True
# config.connect_kwargs.key_filename = '~/.ssh/neahtta'

config.real_hostname = socket.gethostname()

def available_projects():
    """ Find all existing projects which can be included as an env
    argument. That is, "sanit", "sanat", "baakoeh", etc... """
    conf_suffix = ".config.yaml.in"

    return [
        p.name[0 : -len(conf_suffix)]
        for p in Path("configs").glob(f"*{conf_suffix}")
    ]


@task(aliases=available_projects())
def __set_proj(ctx):
    """ Set the project. This is aliased to whatever existing project
    names there are. """
    config.project = sys.argv[1]

    config.clean_first = False
    host = socket.gethostname()

    if host in running_service:
        has_restriction = sum(location_restriction_notice.values(), [])
        if config.project in has_restriction:
            host_rest = location_restriction_notice.get(host, False)
            if host_rest:
                if config.project not in host_rest:
                    print(colored(
                        f"{config.project} is not on the current host <{host}>.", "red"), file=sys.stderr)
                    cont = raw_input(colored('Continue anyway? [y/N] \n', "red"))
                    if not (cont == 'Y' or cont == "y"):
                        sys.exit()


def config_local(*args, **kwargs):
    """ Run a command using the local environment. """
    import os

    config.host = "localhost"
    config.user = None

    config.path_base = os.getcwd()
    config.svn_path = os.environ["GTHOME"]

    config.dict_path = os.path.join(config.path_base, 'dicts')
    config.neahtta_path = config.path_base
    config.i18n_path = os.path.join(config.path_base, 'translations')

    # Make command needs to include explicit path to file, because of
    # fabric.
    config.make_cmd = "make -C %s -f %s" % (
        config.dict_path, os.path.join(config.dict_path, 'Makefile'))
    config.remote_no_fst = False

config_local()


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


def update_gtsvn(ctx):
    print(colored("** svn up **", "cyan"))

    with ctx.cd(config.svn_path):
        p = os.path.join(config.svn_path, "words")
        try:
            ctx.run(f"svn up {p}")
        except Exception:
            return False

    return True


@task
def update_repo(ctx):
    """ Pull repository to update files """
    with ctx.cd(config.neahtta_path):
        print(colored("** git pull **", "cyan"))
        ctx.run("git pull")


def read_config(proj):
    import yaml

    def gettext_yaml_wrapper(loader, node):
        return node.value

    yaml.add_constructor('!gettext', gettext_yaml_wrapper)

    _path = f"configs/{proj}.config.yaml"

    try:
        with open(_path) as f:
            return yaml.load(f, yaml.Loader)
    except (PermissionError, FileNotFoundError):
        pass

    if config.real_hostname not in running_service:
        _path = f"configs/{proj}.config.yaml.in"
        print(colored("** Production config not found, using development (*.in)", "yellow"))
    else:
        print(colored("** Production config not found, and on a production server. Exiting.", "red"))
        sys.exit()

    try:
        with open(_path) as f:
            return yaml.load(f, yaml.Loader)
    except (PermissionError, FileNotFoundError):
        print(colored("** Development config (*.in) does not exist or is not readable, aborting.", "red"))
        sys.exit()


@task
def restart_service(ctx):
    """ Restarts the service. """
    dictionary = config.project

    if config.real_hostname not in running_service:
        print(colored("Services only available live on gtdict.uit.no", "green"))
        sys.exit()

    with ctx.cd(config.neahtta_path):
        print(colored(f"** Restarting service for <{dictionary}> **", "cyan"))
        restart = ctx.run(f"sudo service nds-{dictionary} restart")
        if restart.failed:
            print(colored(f"** Something went wrong while restarting <{dictionary}> **", "red"))
        else:
            print(colored("** <{dictionary}> Service restarted successfully **", "green"))


@task
def compile_dictionary(ctx):
    """ Compile a dictionary project on the server, and restart the
    corresponding service.

        $ fab compile-dictionary [-d DICT]
    """

    failed = False
    dictionary = config.project

    update_gtsvn(ctx)

    with ctx.cd(config.dict_path):
        result = ctx.run(f"{config.make_cmd} {dictionary}-lexica")

        if result.failed:
            print(colored(f"** Something went wrong while compiling <{dictionary}> **"), "red")


@task
def compile(ctx):
    """ Compile a dictionary, fsts and lexica, on the server.

        $ fab compile [-d DICT]

        NB: if the hostname is gtdict.uit.no (set in no_fst_install
        list above), only the lexicon will be compiled, FSTs will not be
        compiled or installed.
    """

    hup = False
    failed = False
    dictionary = config.project

    print(colored(f"Executing on <{config.real_hostname}>", "cyan"))

    update_gtsvn(ctx)

    with ctx.cd(config.dict_path):
        if config.real_hostname in no_fst_install or config.remote_no_fst:
            print((colored("** Skip FST compile for gtdict **", "yellow")))
            print((colored(f"** Compiling lexicon for <{dictionary}> **", "cyan")))
            result = ctx.run(f"{config.make_cmd} {dictionary}-lexica")
            skip_fst = True
        else:
            skip_fst = False

            print(
                colored("** Compiling lexicon and FSTs for <%s> **" % dictionary, "cyan"))

            if config.clean_first in ['Y', 'y']:
                clean_result = ctx.run(config.make_cmd + " %s-clean" % dictionary)

            result = ctx.run(config.make_cmd + " %s" % dictionary)

        if not skip_fst and not result.ok:
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
    dictionary = config.project

    # TODO: need a make path to clean existing dictionary
    with ctx.cd(config.dict_path):
        print((colored(f"** Compiling FST for <{iso}> **", "cyan")))

        clear_tmp = ctx.run(f"{config.make_cmd} rm-{iso}")
        make_fsts = ctx.run(f"{config.make_cmd} {iso}")
        make_fsts = ctx.run(f"{config.make_cmd} {config.project}-{iso}-install")

        if make_fsts.failed:
            print(colored(f"** Something went wrong while compiling <{iso}> **", "red"))
        else:
            print(colored(f"** FST <{iso}> compiled **", "cyan"))

@task
def test_configuration(ctx):
    """ Test the configuration and check language files for errors. """

    _path = f"configs/{config.project}.config.yaml"

    try:
        with open(_path) as f:
            pass
    except FileNotFoundError:
        if config.read_hostname in running_service:
            print(colored("** Production config not found, and on a production server, aborting.", "yellow"))
            sys.exit()

        _path = f"configs/{config.project}.config.yaml.in"
        with open(_path) as f:
            pass

        print(colored("** Production config not found, using development (*.in)", "yellow"))

    # TODO: this assumes virtualenv is enabled, need to explicitly enable
    with ctx.cd(config.neahtta_path):
        print(colored(f"** Checking paths and testing XML for <{config.project}> **", "cyan"))

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
            _y = yaml.load(F, yaml.Loader)
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
            _y = yaml.load(F, yaml.Loader)
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


def run_development_server(ctx):
    """ Run the development server."""
    config_path = Path(f"configs/{config.project}.config.yaml")

    if not config_path.exists():
        config_path = Path(f"configs/{config.project}.config.yaml.in")
        if not config_path.exists():
            print(colored(f"No configuration file found for {config.project}, aborting.", "red"))
            sys.exit()
        print(colored(f"Production config not found, using development (*.in)", "yellow"))

    print(colored("** Starting development server...", "green"))
    run_cmd = ctx.run(f"NDS_CONFIG={config_path} python neahtta.py dev")
    if run_cmd.failed:
        print((colored("** Starting failed for some reason.", "red")))


@task(aliases=["dev"])
def runserver(ctx):
    run_development_server(ctx)

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

    config_path = f"configs/{config.project}.config.yaml.in"
    with ctx.cd(config.config_path):
        print(colored(f"** Running tests for {config.project}", "cyan"))

        test_cmd = ctx.run(f"NDS_CONFIG={config_path} python -m unittest tests.yaml_tests")
        if test_cmd.failed:
            print(colored(f"** Something went wrong while testing <{config.project}> **", "red"))


@task
def test(ctx):
    doctest(ctx)
    test_project(ctx)


@task(aliases=["server-status"])
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
        "sanat.oahpa.no",
    ]

    from concurrent.futures import ThreadPoolExecutor, as_completed
    from urllib.request import urlopen, URLError

    def worker(url, timeout):
        try:
            with urlopen(url, timeout=timeout) as resp:
                status = resp.status
                color = "green" if status == 200 else "red"
                return color, str(status)
        except URLError as e:
            return "red", f"ERROR: {str(e)}"

    with ThreadPoolExecutor() as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = { executor.submit(worker, f"http://{url}", 5): url for url in hosts }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            color, msg = future.result()
            print(colored(f"{msg} {url}", color))


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
