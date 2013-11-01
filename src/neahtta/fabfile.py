""" Tools for compiling dictionaries automatically.

Fabric will automatically execute sets of commands remotely, and will
log in via SSH automatically to do this, assuming you have the proper
credentials.

To install Fabric, follow the instructions on the website:

    http://fabfile.org/

Then run the following to check that it works.

    fab --list

## Basic commands

This is a list of commands to automatize the management of
NDS. Basic operations are listed below, however with some hints:

    $ fab compile_dictionary:valks
    $ fab compile_dictionary:vada

    $ fab compile_fst:crk

    etc...

NB: no gtoahpa targets here yet.


# TODO: fix permissions?

group permissions for neahtta to /opt/smi/LANG/

chmod -R g+w /opt/smi/LANG/
chgrp -R neahtta /opt/smi/LANG/

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

from fabric.colors import red, green, cyan

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
    env.make_cmd = "make -f " + os.path.join(env.dict_path, 'Makefile')

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

    env.make_cmd = "make -f " + os.path.join(env.dict_path, 'Makefile')


@task
def update_gtsvn():
    with cd(env.svn_path):
        print(cyan("** svn up **"))
        env.run('svn up gt gtcore langs words')

@task
def restart_service(dictionary='x'):
    """ Restarts the services.
    """

    # TODO: need to be another user to run sudo service nds-* stop ;
    # start

    fail = False
    if env.real_hostname not in running_service:
        print(green("** No need to restart, nds-<%s> not available on this host. **" % dictionary))
        return

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
def compile_dictionary(dictionary='x'):
    """ Compile a dictionary project on the server, and restart the
    corresponding service.

        $ fab compile_dictionary:DICT

    # TODO: restarting doesn't actually work yet.

    """

    hup = False
    failed = False

    update_gtsvn()

    print env.dict_path
    with cd(env.dict_path):
        env.run("svn up Makefile")

        result = env.run(env.make_cmd + " %s-lexica" % dictionary)

        if not result.failed:
            hup = True
        else:
            failed = True

    if hup:
        restart_service(dictionary)

    if failed:
        print(red("** Something went wrong while compiling <%s> **" % dictionary))

@task
def compile(dictionary='x'):
    """ Compile a dictionary, fsts and lexica, on the server.

        $ fab compile:DICT
    """

    hup = False
    failed = False

    update_gtsvn()

    # TODO: need a make path to clean existing dictionary
    with cd(env.dict_path):
        env.run("svn up Makefile")

        print(cyan("** Compiling lexicon and FSTs for <%s> **" % dictionary))
        result = env.run(env.make_cmd + " %s" % dictionary)

        if not result.failed:
            hup = True
            print(cyan("** Installing FSTs for <%s> **" % dictionary))
            result = env.run(env.make_cmd + " %s-install" % dictionary)
            if not result.failed:
                hup = True
            else:
                failed = True
        else:
            failed = True

    if hup:
        restart_service(dictionary)

    if failed:
        print(red("** Something went wrong while compiling <%s> **" % dictionary))

@task
def compile_fst(iso='x'):
    """ Compile a dictionary project on the server.

        $ fab compile_dictionary:DICT
    """

    hup = False

    # update_gtsvn()

    # TODO: need a make path to clean existing dictionary
    with cd(env.dict_path):
        # env.run("svn up Makefile")
        print(cyan("** Compiling FST for <%s> **" % iso))

        clear_tmp = env.run(env.make_cmd + " rm-%s" % iso)

        make_fsts = env.run(env.make_cmd + " %s" % iso)

        if make_fsts.failed:
            print(red("** Something went wrong while compiling <%s> **" % iso))
        else:
            print(cyan("** FST <%s> compiled **" % iso))

