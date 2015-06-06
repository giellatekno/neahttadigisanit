"""
A fabfile for executing gtcore/build commands remotely, and then copying
the build result locally over SSH. Must have SSH keys installed for this
to work, including passwords somehow is a baaaad idea.

    fab LOCATION/user DICT TASKS

NB: remote compile only really works with HFST.

"""



import os, sys

from fabric.decorators import roles

from fabric.api import ( cd
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
    env.hosts = ['neahtta@gtweb.uit.no']
    env.path_base = '/home/neahtta'

    env.svn_path = env.path_base + '/gtsvn'
    env.gtcore_svn_path = env.path_base + '/gtsvn/gtcore'
    # env.path_to_lang = env.svn_path + '/' + env.compile_langs

    # env.make_cmd = "make -C %s -f %s" % ( env.path_to_lang
    #                                     , os.path.join(env.dict_path, 'Makefile')
    #                                     )
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
        'gtcore/',
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
    print(cyan("** Compiling gtcore **"))
    gtcore = env.svn_path + 'gtcore/'
    with cd(gtcore):
        make_file = env.svn_path + 'gtcore/Makefile'
        make_ = "make -C %s -f %s" % ( gtcore
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

    for p in svn_langs:
        copy_result(p)

def copy_result(path):
    local('rsync -avz --include')
    # rsync -a root@somewhere:/folder/remote/*.{hfst,hfstol} .

    # certain suffixes

@task
def compile_fst(iso='x'):
    """ Compile a dictionary project on the server.

        $ fab compile_dictionary:DICT

    """

    hup = False

    path_to_lang = os.path.join(env.svn_path,  'langs/' + iso)

    with cd(path_to_lang):

        make_cmd = "make -C %s -f %s" % ( path_to_lang
                                        , os.path.join(path_to_lang, 'Makefile')
                                        )

        # env.run("svn up Makefile")
        print(cyan("** Compiling FST for <%s> **" % iso))

        _exists = os.path.join(path_to_lang, 'configure')
        if env.local:
            skip_autogen = os.path.exists(_exists)
        else:
            skip_autogen = exists(_exists)

        if not skip_autogen:
            # test for need to autogen: `configure` exists?
            autogen = env.run('cd %s && ./autogen.sh' % path_to_lang)

            if autogen.failed:
                print(red("** Something went wrong while running autogen <%s> **" % iso))
                sys.exit()

        configure = env.run('cd ' + path_to_lang + ' && ./configure ' + env.configure_opts)

        if configure.failed:
            print(red("** Something went wrong while running ./configure <%s> **" % iso))
            print(cyan("**   ./configure " + env.configure_opts))

        make_fst = env.run(make_cmd)
        sys.exit()


        if make_fsts.failed:
            print(red("** Something went wrong while compiling <%s> **" % iso))
        else:
            print(cyan("** FST <%s> compiled **" % iso))

