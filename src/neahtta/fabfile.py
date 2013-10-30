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

from fabric.decorators import roles
from fabric.api import ( cd
                       , run
                       , env
                       )
from fabric.operations import ( sudo )

from fabric.colors import red, green, cyan

env.roledefs.update({
    'gtweb': ['neahtta@gtweb.uit.no',],
})

env.hosts = ['neahtta@gtweb.uit.no',]

env.use_ssh_config = True
# env.key_filename = '~/.ssh/neahtta'

USER_PATH = '/home/neahtta'
SVN_PATH = USER_PATH + '/gtsvn'
DICT_PATH = USER_PATH + '/neahtta/dicts'
NEAHTTA_PATH = USER_PATH + '/neahtta'
I18N_PATH = USER_PATH + '/neahtta/translations'

@roles('gtweb')
def update_gtsvn():
    with cd(SVN_PATH):
        print(cyan("** svn up **"))
        run('svn up gt gtcore langs words')

@roles('gtweb')
def restart_service(dictionary='x'):
    """ Restarts the services.
    """

    # TODO: need to be another user to run sudo service nds-* stop ;
    # start

    fail = False
    with cd(NEAHTTA_PATH):
        print(cyan("** Restarting service for <%s> **" % dictionary))
        stop = run("sudo service nds-%s stop" % dictionary)
        if not stop.failed:
            start = run("sudo service nds-%s start" % dictionary)
            if not start.failed:
                print(green("** <%s> Service has restarted successfully **" % dictionary))
            else:
                fail = True
        else:
            fail = True

    if fail:
        print(red("** something went wrong while restarting <%s> **" % dictionary))

@roles('gtweb')
def update_translations():

    with cd(I18N_PATH):
        run('svn up')

    with cd(NEAHTTA_PATH):
        run('pybabel compile -d translations')

    hup_all()

@roles('gtweb')
def compile_dictionary(dictionary='x'):
    """ Compile a dictionary project on the server, and restart the
    corresponding service.

        $ fab compile_dictionary:DICT

    # TODO: restarting doesn't actually work yet.

    """

    hup = False
    failed = False

    update_gtsvn()

    with cd(DICT_PATH):
        print(cyan("** Compiling lexicon <%s> **" % dictionary))
        run("svn up Makefile")
        make_clean = run("make rm-%s-lexica" % dictionary)

        result = run("make %s-lexica" % dictionary)

        if not result.failed:
            hup = True
        else:
            failed = True

    if hup:
        restart_service(dictionary)

    if failed:
        print(red("** Something went wrong while compiling <%s> **" % dictionary))

@roles('gtweb')
def compile(dictionary='x'):
    """ Compile a dictionary, fsts and lexica, on the server.

        $ fab compile:DICT
    """

    hup = False
    failed = False

    update_gtsvn()

    # TODO: need a make path to clean existing dictionary
    with cd(DICT_PATH):
        run("svn up Makefile")

        print(cyan("** Compiling lexicon and FSTs for <%s> **" % dictionary))
        result = run("make %s" % dictionary)

        if not result.failed:
            hup = True
            print(cyan("** Installing FSTs for <%s> **" % dictionary))
            result = run("make %s-install" % dictionary)
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

@roles('gtweb')
def compile_fst(iso='x'):
    """ Compile a dictionary project on the server.

        $ fab compile_dictionary:DICT
    """

    hup = False

    update_gtsvn()

    # TODO: need a make path to clean existing dictionary
    with cd(DICT_PATH):
        run("svn up Makefile")
        print(cyan("** Compiling FST for <%s> **" % iso))
        make_fsts = run("make %s" % iso)
        if make_fsts.failed:
            print(red("** Something went wrong while compiling <%s> **" % iso))
        else:
            print(cyan("** FST <%s> compiled **" % iso))

