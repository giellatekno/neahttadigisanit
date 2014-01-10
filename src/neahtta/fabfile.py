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

    $ fab local baakoeh compile_dictionary

To do the same remotely, and restart the service, you would run:

    $ fab gtweb sanat compile_dictionary restart_service

With the latter, Fabric will connect via SSH and run commands remotely.
You may be asked for your SSH password.

"""

import os

from fabric.decorators import roles

from fabric.api import ( cd
                       , run
                       , local
                       , env
                       , task
                       )

from fabric.operations import ( sudo )

from fabric.colors import red, green, cyan, yellow

env.no_svn_up = False
env.use_ssh_config = True
# env.key_filename = '~/.ssh/neahtta'

import socket
env.real_hostname = socket.gethostname()

# Hosts that have an nds- init.d script
running_service = [
    'gtweb.uit.no',
    'gtlab.uit.no',
    'gtoahpa.uit.no'
]

# set up environments
# Assume local unless otherwise noted

@task
def baakoeh():
    """ Configure for baakoeh """
    # TODO: change on gtoahpa.uit.no: compile only does dictionary, not
    # fst
    env.current_dict = "baakoeh"

@task
def sanit():
    """ Configure for sanit """
    # TODO: change on gtoahpa.uit.no: compile only does dictionary, not
    # fst
    env.current_dict = "sanit"

@task
def valks():
    """ Configure for valks """
    env.current_dict = "valks"

@task
def guusaaw():
    """ Configure for guusaaw """
    env.current_dict = "guusaaw"

@task
def kyv():
    """ Configure for kyv """
    env.current_dict = "kyv"

@task
def muter():
    """ Configure for muter """
    env.current_dict = "muter"

@task
def no_svn_up():
    """ Configure for muter """
    env.no_svn_up = True

@task
def pikiskwewina():
    """ Configure for pikiskwewina """
    env.current_dict = "pikiskwewina"

@task
def saan():
    """ Configure for saan """
    env.current_dict = "saan"

@task
def sanat():
    """ Configure for sanat """
    env.current_dict = "sanat"

@task
def vada():
    """ Configure for vada """
    env.current_dict = "vada"


@task
def local(*args, **kwargs):
    """ Run a command using the local environment.
    """
    from fabric.operations import local as lrun
    import os

    env.run = lrun
    env.hosts = ['localhost']

    gthome = os.environ.get('GTHOME')
    env.path_base = os.getcwd()

    env.svn_path = gthome
    env.dict_path = os.path.join(env.path_base, 'dicts')
    env.neahtta_path = env.path_base
    env.i18n_path = os.path.join(env.path_base, 'translations')

    # Make command needs to include explicit path to file, because of
    # fabric.
    env.make_cmd = "make -C %s -f %s" % ( env.dict_path
                                        , os.path.join(env.dict_path, 'Makefile')
                                        )

@task
def gtweb():
    """ Run a command remotely on gtweb
    """
    env.run = run
    env.hosts = ['neahtta@gtweb.uit.no']
    env.path_base = '/home/neahtta'

    env.svn_path = env.path_base + '/gtsvn'
    env.dict_path = env.path_base + '/neahtta/dicts'
    env.neahtta_path = env.path_base + '/neahtta'
    env.i18n_path = env.path_base + '/neahtta/translations'

    env.make_cmd = "make -C %s -f %s" % ( env.dict_path
                                        , os.path.join(env.dict_path, 'Makefile')
                                        )

@task
def gtoahpa():
    """ Run a command remotely on gtweb
    """
    env.run = run
    env.hosts = ['neahtta@gtoahpa.uit.no']
    env.path_base = '/home/neahtta'

    env.svn_path = env.path_base + '/gtsvn'
    env.dict_path = env.path_base + '/neahtta/dicts'
    env.neahtta_path = env.path_base + '/neahtta'
    env.i18n_path = env.path_base + '/neahtta/translations'

    env.make_cmd = "make -C %s -f %s" % ( env.dict_path
                                        , os.path.join(env.dict_path, 'Makefile')
                                        )

@task
def update_gtsvn():
    if env.no_svn_up:
        print(yellow("** skipping svn up **"))
        return

    with cd(env.svn_path):
        paths = [
            'gt/',
            'gtcore/',
            'langs/',
            'words/',
        ]
        print(cyan("** svn up **"))
    for p in paths:
        _p = os.path.join(env.svn_path, p)
        with cd(_p):
            env.run('svn up ' + _p)

@task
def restart_service(dictionary=False):
    """ Restarts the services.
    """

    if not dictionary:
        dictionary = env.current_dict

    fail = False

    # Not a big issue, but figure this out for local development.
    # if env.real_hostname not in running_service:
    #     print env.real_hostname
    #     print(green("** No need to restart, nds-<%s> not available on this host. **" % dictionary))
    #     return

    with cd(env.neahtta_path):
        print(cyan("** Restarting service for <%s> **" % dictionary))
        stop = env.run("sudo service nds-%s stop" % dictionary)
        if not stop.failed:
            start = env.run("sudo service nds-%s start" % dictionary)
            if not start.failed:
                print(green("** <%s> Service has restarted successfully **" % dictionary))
            else:
                fail = True
        else:
            fail = True

    if fail:
        print(red("** something went wrong while restarting <%s> **" % dictionary))

@task
def update_translations():

    with cd(env.i18n_path):
        env.run('svn up')

    with cd(env.neahtta_path):
        env.run('pybabel compile -d translations')

    hup_all()

@task
def compile_dictionary(dictionary=False, restart=False):
    """ Compile a dictionary project on the server, and restart the
    corresponding service.

        $ fab compile_dictionary:DICT

    # TODO: restarting doesn't actually work yet.

    """

    failed = False

    if not dictionary:
        dictionary = env.current_dict

    update_gtsvn()

    with cd(env.dict_path):
        env.run("svn up Makefile")

        result = env.run(env.make_cmd + " %s-lexica" % dictionary)

        if result.failed:
            failed = True

    if restart:
        restart_service(dictionary)

    if failed:
        print(red("** Something went wrong while compiling <%s> **" % dictionary))

@task
def compile(dictionary=False,restart=False):
    """ Compile a dictionary, fsts and lexica, on the server.

        $ fab compile:DICT

        NB: if the hostname is gtoahpa.uit.no, only the lexicon will be
        compiled
    """

    hup = False
    failed = False

    print(cyan("Executing on <%s>" % env.host))

    if not dictionary:
        dictionary = env.current_dict

    update_gtsvn()

    # TODO: need a make path to clean existing dictionary
    with cd(env.dict_path):
        if env.no_svn_up:
            print(yellow("** Skipping svn up of Makefile"))
        else:
            env.run("svn up Makefile")

        if env.real_hostname == 'gtoahpa.uit.no':
            print(yellow("** Skip FST compile for gtoahpa **"))
            print(cyan("** Compiling lexicon for <%s> **" % dictionary))
            result = env.run(env.make_cmd + " %s-lexica" % dictionary)
            skip_fst = True
        else:
            skip_fst = False
            print(cyan("** Compiling lexicon and FSTs for <%s> **" % dictionary))
            result = env.run(env.make_cmd + " %s" % dictionary)

        if not result.failed:
            if not skip_fst:
                print(cyan("** Installing FSTs for <%s> **" % dictionary))
                result = env.run(env.make_cmd + " %s-install" % dictionary)
                if result.failed:
                    failed = True
        else:
            failed = True

    if restart:
        restart_service(dictionary)

    if failed:
        print(red("** Something went wrong while compiling <%s> **" % dictionary))
    else:
        print(cyan("** <%s> FSTs and Lexicon compiled okay, should be safe to restart. **" % dictionary))

@task
def compile_fst(iso='x'):
    """ Compile a dictionary project on the server.

        $ fab compile_dictionary:DICT
    """

    hup = False

    dictionary = env.current_dict

    update_gtsvn()

    # TODO: need a make path to clean existing dictionary
    with cd(env.dict_path):
        # env.run("svn up Makefile")
        print(cyan("** Compiling FST for <%s> **" % iso))

        clear_tmp = env.run(env.make_cmd + " rm-%s" % iso)

        make_fsts = env.run(env.make_cmd + " %s" % iso)
        make_fsts = env.run(env.make_cmd + " %s-%s-install" % (dictionary, iso))

        if make_fsts.failed:
            print(red("** Something went wrong while compiling <%s> **" % iso))
        else:
            print(cyan("** FST <%s> compiled **" % iso))

@task
def test_configuration():
    # TODO: this assumes virtualenv is enabled, need to explicitly enable
    _dict = env.current_dict
    with cd(env.dict_path):
        print(cyan("** Checking paths and testing XML for <%s> **" % _dict))

        cmd ="NDS_CONFIG=configs/%s.config.yaml python manage.py chk-fst-paths"
        test_cmd = env.run(cmd % _dict)
        if test_cmd.failed:
            print(red("** Something went wrong while testing <%s> **" % _dict))
        else:
            print(cyan("** Everything seems to work **"))

