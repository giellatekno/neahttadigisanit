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

"""

from fabric.decorators import roles
from fabric.api import ( cd
                       , sudo
                       , run
                       , env
                       )

env.roledefs.update({
    'gtweb': ['neahtta@gtweb.uit.no',],
})

env.use_ssh_config = True

# env.key_filename = '~/.ssh/neahtta'

USER_PATH = '/home/neahtta'
SVN_PATH = USER_PATH + '/gtsvn'
DICT_PATH = USER_PATH + '/neahtta/dicts'
NEAHTTA_PATH = USER_PATH + '/neahtta'
I18N_PATH = USER_PATH + '/neahtta/translations'

@roles('gtweb')
def hup_all():
    """ hup actually won't work with NDS yet, but out of expectation
    that it will eventually, and for familiarity that's what this is
    called.
    """

    # TODO: need to be another user to run sudo service nds-* stop ;
    # start

    with cd(NEAHTTA_PATH):
        run('ls -c1 *.pid')

@roles('gtweb')
def update_gtsvn():
    with cd(SVN_PATH):
        run('svn up gt gtcore langs words')

@roles('gtweb')
def hup_service(dictionary='x'):
    """ hup actually won't work with NDS yet, but out of expectation
    that it will eventually, and for familiarity that's what this is
    called.
    """

    # TODO: need to be another user to run sudo service nds-* stop ;
    # start

    with cd(NEAHTTA_PATH):
        run("ls -c1 %s-pidfile.pid" % dictionary)

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

    update_gtsvn()

    with cd(DICT_PATH):
        run("svn up Makefile")
        make_clean = run("make rm-%s-lexica" % dictionary)

        result = run("make %s-lexica" % dictionary)

        if not result.failed:
            hup = True

    if hup:
        hup_service(dictionary)

@roles('gtweb')
def compile(dictionary='x'):
    """ Compile a dictionary, fsts and lexica, on the server.

        $ fab compile:DICT
    """

    hup = False

    update_gtsvn()

    # TODO: need a make path to clean existing dictionary
    with cd(DICT_PATH):
        run("svn up Makefile")

        result = run("make %s" % dictionary)

        if not result.failed:
            hup = True

    if hup:
        hup_service(dictionary)

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
        make_fsts = run("make %s" % iso)

# TODO: 
#  * fab build-lexicon gtweb DICT
#  * fab build-fst gtweb ISO
#  * fab 
