"""
A fabfile for executing giella-core/build commands remotely, and then copying
the build result locally over SSH. Must have SSH keys installed for this
to work, including passwords somehow is a baaaad idea.

    fab LOCATION/user DICT TASKS

NB: remote compile only really works with HFST.


TODO: finish copy
TODO: work on cmd argument structure
TODO: how to define local copy destination? probably have some defaults
      options, possibility to define in separate options file

TODO: tmux for builds

"""



import os, sys

from fabric.decorators import roles

from fabric.api import ( cd
                       , shell_env
                       , run
                       , local
                       , env
                       , task
                       , settings
                       )

from fabric.operations import ( sudo )

from fabric.colors import red, green, cyan, yellow

from fabric.contrib.console import confirm
from fabric.contrib.files import exists

from fabric.utils import abort

# Default settings
env.configure_opts = "--without-xfst --with-hfst --enable-dicts"

env.user = "pyry"
env.hosts = ['localhost']

env.no_svn_up = False
env.use_ssh_config = True
# TODO:
# env.key_filename = '~/.ssh/neahtta'

def get_projects(svn_path):
    """ Find all existing projects which can be included as an env
    argument """
    import os

    exclusions = ['autom4te.cache', 'build']

    avail_projects = []

    langs = [l for l in next(os.walk(svn_path + '/langs'))[1] if l not in exclusions]

    return langs



@task
def local(*args, **kwargs):
    from fabric.operations import local as lrun

    gthome = os.environ.get('GTHOME')

    env.run = lrun
    env.local = True
    env.path_base = os.getcwd()

    env.svn_path = gthome
    env.dict_path = os.path.join(env.path_base, 'dicts')
    env.neahtta_path = env.path_base
    env.i18n_path = os.path.join(env.path_base, 'translations')

    # Make command needs to include explicit path to file, because of
    # fabric.

    # env.make_cmd = "make -C %s -f %s" % ( env.dict_path
    #                                     , os.path.join(env.dict_path, 'Makefile')
    #                                     )

    env.compile_langs = []
    env.available_langs = get_projects(env.svn_path)
    return env, env.available_langs



# TODO:
env, langs = local()

@task(aliases=langs)
def set_langs():
    avail_projects = env.available_langs

    proj_arg = [a for a in sys.argv if a in avail_projects]

    env.compile_langs = proj_arg
    print env.compile_langs
    return proj_arg

# Hosts that we can compile on
remote_compilers = [
    'gtweb.uit.no',
    'gtlab.uit.no',
]

# set up environments
# Assume local unless otherwise noted


@task
def no_svn_up():
    """ Do not SVN up """
    env.no_svn_up = True

@task
def gtweb():
    """ Run a command remotely on gtweb
    """
    env.run = run
    env.local = False
    # TODO: icall
    env.user = 'neahtta'
    env.hosts = ['neahtta@gtweb.uit.no']
    env.current_host = 'gtweb.uit.no'
    env.path_base = '/home/neahtta'

    env.svn_path = env.path_base + '/gtsvn'
    env.giella-core_svn_path = env.path_base + '/gtsvn/giella-core'

@task
def gtlab():
    # TODO:
    pass

# TODO: fix
@task
def svn_up():
    """ SVN up the config files """
    if env.no_svn_up:
        print(yellow("** skipping svn up **"))
        return

    svn_lang_paths = [ 'langs/%s' % l for l in env.compile_langs ]

    paths = [
        'giella-core/',
    ] + svn_lang_paths

    print paths

    print(cyan("** svn up **"))

    # TODO: do these all at once?
    for p in paths:
        _p = os.path.join(env.svn_path, p)
        try:
            svn_up_cmd = env.run('svn up ' + _p)
        except:
            abort(
                red("\n* svn up failed in <%s>. Prehaps the tree is locked?" % _p) + '\n' + \
                red("  Correct this (maybe with `svn cleanup`) and rerun the command, or run with `no_svn_up`.")
            )

    sys.exit()

    # TODO: necessary to run autogen just in case? 
    print(cyan("** Compiling giella-core **"))
    giella-core = env.svn_path + 'giella-core/'
    with cd(giella-core):
        make_file = env.svn_path + 'giella-core/Makefile'
        make_ = "make -C %s -f %s" % ( giella-core
                                     , make_file
                                     )
        result = env.run(make_)

@task
def compile_langs():
    """ Compile fsts.
    """

    svn_langs = env.compile_langs

    failed = False

    # TODO: 
    # print(cyan("Executing on <%s>" % env.real_hostname))

    # svn_up()

    for p in svn_langs:
        compile_fst(p)

@task
def copy_only():

    svn_langs = env.compile_langs

    failed = False

    for p in svn_langs:
        copy_result(p)

def copy_result(path):
    if env.local:
        return True

    j = os.path.join

    user = env.user

    source = j(
        env.svn_path, j('langs', j(path, 'src'))
    )

    target = j(
        os.environ.get('GTHOME'), j('langs',  j(path, 'src'))
    )

    host = env.current_host

    # TODO: why doesn't rsync actually want to run?
    rsync_cmd = """rsync -avz -e ssh --no-motd --include="*.hfst" --include="*.hfstol" """
    rsync_cmd += "%(user)s@%(host)s:%(source)s %(target)s""" % locals()

    local(rsync_cmd)

@task
def compile_fst(iso='x'):
    """ Compile a dictionary project on the server.

        $ fab compile_dictionary:DICT

    """

    hup = False

    path_to_lang = os.path.join(env.svn_path,  'langs/' + iso)

    tmux_session_id = "build-langs-%s"

    with cd(path_to_lang):


        # TODO: check if tmux is available
        # TODO: if available, check if session exists, and attach to
        # that if it is still running.

        ## with shell_env(TMUX=''):
        ##     test = env.run('tmux attach -t sess')
        ##     if test.failed:
        ##         print(red('failed'))

        print(cyan("** Compiling FST for <%s> **" % iso))

        _exists = os.path.join(path_to_lang, 'configure')
        if env.local:
            skip_autogen = os.path.exists(_exists)
        else:
            skip_autogen = exists(_exists)

        if not skip_autogen:
            autogen = env.run('cd %s && ./autogen.sh' % path_to_lang)
            if autogen.failed:
                print(red("** Something went wrong while running autogen <%s> **" % iso))
                sys.exit()

        configure = env.run('cd ' + path_to_lang + ' && ./configure ' + env.configure_opts)

        if configure.failed:
            print(red("** Something went wrong while running ./configure <%s> **" % iso))
            print(cyan("**   ./configure " + env.configure_opts))

        # TODO: add a pane with an explanation of what this is, incase
        # anyone else is using this

        make_cmd = "make -C %s -f %s" % ( path_to_lang
                                        , os.path.join(path_to_lang, 'Makefile')
                                        )

        with shell_env(TMUX=''):
            print(cyan("Running build in a tmux session. If the ssh connection "))
            print(cyan("is interrupted due to bad network, then build will continue"))

            build_cmd = env.run('tmux new -s ' + tmux_session_id + ' "' + make_cmd + '"')

            if build_cmd.failed:
                print(red("** Something went wrong while running make, or connection was lost **" % iso))

# TMUX ideation scratch
# env.run('tmux new -s build-123 -d')
# with prefix('tmux send-keys -t "build-123:0.0" '):
#     env.run('echo omg')

# env.run('tmux new-session -d -s build-123')
# env.run('tmux send-keys -t build-123:0 echo zomg')
# env.run('tmux attach -t build-123')
