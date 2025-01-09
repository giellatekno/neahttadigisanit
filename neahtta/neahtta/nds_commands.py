"""Neahttadigisanit management tool for updating dictionaries, restarting the
server, running the development server, and such things."""

# See the EXAMPLES below the imports

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from functools import partial
from shlex import split as split_cmd

from termcolor import colored

from neahtta.config import Config

EXAMPLES = """Examples:

Update a dictionary:
    # 1: update dictionary sources  (pulls dict repositories from github)
    $ nds update sanit

    # 2: compile new dictionary   (merges dictionary src/ into final .xml file)
    $ nds compile sanit

    # 3: update the service to reflect the changes
    $ nds restart sanit

Adding stem to smenob:
    $ nds add-stem
"""

RED = partial(colored, color="red")
GREEN = partial(colored, color="green")
CYAN = partial(colored, color="cyan")

PROD_HOSTNAME = "gtdict.uit.no"
PROD_HOSTNAME_02 = "gtdict-02"
HOSTNAME = socket.gethostname()

# I can never remember which one it is.. so just make all of these work
# The first one is the "primary" name of the command
UPDATE_DICTS_ALIASES = [
    "update",
    "up",
    "update-dict",
    "update-dicts",
    "update-dictionary",
    "update-dictionaries",
]

COMPILE_DICTS_ALIASES = [
    "compile",
    "compile-dict",
    "compile-dicts",
    "compile-dictionary",
    "compile-dictionaries",
]


def require_gut():
    # anders: the version of gut I have installed locally on my machine has
    # not yet been updated to support --format=json, so to run it
    # locally, I need to be able to pass path to my gut binary
    if custom_gut_binary := os.environ.get("GUT_BINARY"):
        gut_path = Path(custom_gut_binary).resolve()
        if not gut_path.exists():
            sys.exit(
                "custom gut path given in environment variable "
                "GUT_BINARY does not exist"
            )
    else:
        gut_path = shutil.which("gut")
        if gut_path is None:
            sys.exit(
                "Fatal: cannot find `gut` using `which`. (If it is installed "
                "in a non-standard location, pass the path to the gut binary "
                "in the GUT_BINARY environment variable)"
            )

    gut_app_toml_path = Path.home() / ".config" / "gut" / "app.toml"
    gut_app_toml_path = gut_app_toml_path.resolve()
    gutroot = None
    try:
        with open(gut_app_toml_path) as gut_app_toml:
            for line in gut_app_toml:
                if line.startswith("root"):
                    _, gutroot = line.split("=")
                    gutroot = Path(gutroot.strip()[1:-1]).resolve()
                    break
        if gutroot is None:
            sys.exit(
                "cannot parse app.toml gut config file, maybe try " "reinitializing gut"
            )
    except FileNotFoundError:
        sys.exit("gut is not initialized on this system, aborting.")

    return gutroot, gut_path


GUTROOT, GUT_BINARY = require_gut()


# anders: unused
# it was meant to only give the token to private repos when required, but they
# have instead been set in the repo config (in the url directly).
# But, keeping it for now -- the secret handling is really not good enough,
# and will have to do something at some point in time!!
# def gut_user_toml():
#     config_file_path = Path.home() / ".config" / "gut" / "user.toml"
#     config_file_path = config_file_path.resolve()
#     config = {}
#     with open(config_file_path) as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith("#"):
#                 continue
#             key, value = line.split("=")
#             key = key.strip()
#             value = value.strip()
#             if value.startswith("\"") and value.endswith("\""):
#                 value = value[1:-1]
#             config[key] = value
#     return config


script_directory = GUTROOT / "giellalt" / "giella-core" / "dicts" / "scripts"
sys.path.append(str(script_directory))
from merge_giella_dicts import merge_giella_dicts


def dicts_from_config(config):
    for source, target in config.dictionaries.keys():
        if source != "SoMe" and target != "SoMe":
            yield f"{source}-{target}"


def available_projects(include_inactive=False, include_dicts=False):
    """Find active projects (projects with a config file
    'configs/<project>.config.yaml'). If `all` is True, also includes inactive
    projects (which only has a file 'configs/<project>.config.yaml.in').

    Essentially, "sanit", "sanat", "baakoeh", etc..."""
    suffix = ".config.yaml"
    configs_folder = Path(__file__).parent / "configs"
    projects = {n: [] for n in configs_folder.glob(f"*{suffix}")}

    if include_inactive:
        suffix += ".in"
        projects.update({n: [] for n in configs_folder.glob(f"*{suffix}")})

    if include_dicts:
        import yaml

        for yaml_config_file, dicts in projects.items():
            with open(yaml_config_file) as f:
                conf = yaml.load(f, Loader=yaml.Loader)

            for d in conf.get("Dictionaries", []):
                src = d["source"]
                trg = d["target"]
                dicts.append(f"dict-{src}-{trg}")

    without_suffixes = {}
    for project, dictionaries in projects.items():
        stem = project.stem
        real_stem = stem[0 : stem.index(".")]
        without_suffixes[real_stem] = dictionaries

    return without_suffixes


def list_projects(project="all", include_inactive=False, include_dicts=False):
    data = available_projects(include_inactive, include_dicts)

    # if specific project given, only show data for that project
    if project != "all":
        try:
            data = {project: data[project]}
        except KeyError:
            if not include_inactive:
                hint = "hint: try also listing 'inactive' projects with -i"
            else:
                hint = f"hint: neither 'configs/{project}.config.yaml' nor "
                hint += f"'configs/{project}.config.yaml.in' exists"
            sys.exit(f"unknown project: {project}\n{hint}")

    for project, dictionaries in data.items():
        print(project, end="")
        if dictionaries:
            print(":")
            print(*(f"{d}" for d in dictionaries), sep="\n")
        else:
            print()


def needs_update(xml_files: list[Path], compiled_file: Path):
    """Check if dictionary sources are newer than the compiled_file. If the
    compiled file does not exist, this function will also return True."""
    if not compiled_file.exists():
        return True

    # anders: follow_symlinks argument of Path.stat() added in 3.10
    last_source_mtime = max(file.stat().st_mtime for file in xml_files)
    last_compiled_file_mtime = compiled_file.stat().st_mtime

    return last_source_mtime > last_compiled_file_mtime


def compile_dicts(project, force=None):
    """Compile the merged .xml dictionary file from dictionary sources for
    the given project. By default, if the existing merged file is newer than
    the source directory, that dictionary will be skipped. Use --force to
    override this, and always generate new dictionaries."""

    if project == "all":
        for project in sorted(available_projects()):
            try:
                _compile_dicts(project, force=force)
                print()
            except NotImplementedError:
                print("TODO!")
    else:
        _compile_dicts(project, force=force)


def _run_prepare_script(script, msg, force=False):
    print(msg, end="", flush=True)
    env = dict(os.environ)
    if force:
        # Tell the prepare script to force running (even if it for example
        # by default skips running if output is newer than sources)
        env["PREPARE_SCRIPT_FORCE"] = "yes"
    proc = subprocess.run(script, text=True, capture_output=True, env=env)
    ok = proc.returncode == 0
    if ok:
        print(GREEN("done"))
    else:
        print(RED("failed"), "(script finished with non-0 exit code)")

    if proc.stdout:
        print(f"prepare_script wrote to stdout:\n{proc.stdout}")

    if proc.stderr:
        print(f"prepare_script wrote to stderr:\n{proc.stderr}")

    return ok


def _compile_dicts(project, force=None):
    print(f"** Compiling dictionaries for {project}...")
    config = Config(".")
    config.from_yamlfile(f"neahtta/configs/{project}.config.yaml")

    giellalt_dir = Path(GUTROOT) / "giellalt"

    processed = []
    n = 0
    n_no_updates = 0
    did_smenob = False

    for d in config.dict_entries():
        source, target, compiled_file = d.source, d.target, d.compiled_file

        if d.prepare_script:
            if compiled_file not in processed:
                msg = f"** Run prepare_script of {source}-{target}... "
                ok = _run_prepare_script(d.prepare_script, msg, force=force)
                if not ok:
                    continue

        msg = f"** Merge dictionary {source}-{target} > {compiled_file}... "
        print(msg, end="", flush=True)

        if compiled_file in processed:
            print(CYAN("skipped"), "(already processed)")
            continue

        src_dir = d.src_dir(giellalt_dir)

        try:
            source_files = [f for f in src_dir.iterdir() if f.suffix == ".xml"]
        except OSError as e:
            # not a directory, no such file or directory, permission error, etc
            print(RED("failed"), f"({e})")
            continue

        if not source_files:
            print(RED("failed"), "(no source files)")
            n_no_updates += 1
            continue

        processed.append(compiled_file)

        need = needs_update(source_files, compiled_file)

        if not need and not force:
            print(CYAN("skipped"), "(no updates)")
            n_no_updates += 1
        else:
            n_entries = merge_giella_dicts(src_dir, compiled_file.resolve())
            n += 1
            print(GREEN("done"), f"({n_entries} entries total)")
            if source == "sme" and target == "nob":
                did_smenob = True

    if n_no_updates > 0:
        print(
            f"\n{n_no_updates} dictionaries were skipped because the existing "
            "built dictionary file is newer than the xml source files.\n\n"
            "Hint: To force rebuilding all dictionaries without checking "
            "modification times, run:\n"
            f"  nds compile {project} -f    (or: nds compile {project} --force)\n"
            f"Hint: If you expected updates to happen, try to update the "
            "underlying git repositories of the dictionaries, by running:\n"
            f"  nds update {project}\n"
            f"...then re-run this command (nds compile {project})"
        )

    if did_smenob:
        print(
            "\n!! sme-nob: dictionary has been updated, you probably want "
            "to add stems to it. If so, run:\n  nds add-stem"
        )


def autoupdate(force=False):
    """For all instances, pull new dictionarie sources from git, and compile
    and restart the instance if there are updates."""
    for project in available_projects():
        print(f"Processing {project}...")
        print("Pulling git repositories...")
        statuses = pull_repos_for_project(project, use_gut=False)
        print("Done pulling git repositories...")
        if all(status == "Nothing" for d, status in statuses.items()):
            print(f"{project}: all dictionaries up to date")
            if not force:
                continue

        if any(status.startswith("error") for d, status in statuses.items()):
            print(f"{project}: errors during git pull, continuing to next")
            continue

        # There are some updates, but I need to make sure I can compile
        compile_dicts(project, force=force)

        if Path("/etc/systemd/system/nds-{project}.service").exists():
            _restart_systemd_service(project)
        else:
            print(f"{project}: No systemd service to restart")


def git_pull(repo):
    cmd = split_cmd(f"git -C {repo} pull")
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return "git: pull timeout"

    stdout = proc.stdout

    if "Already up to date." in stdout:
        return "Nothing"
    elif "Fast-forward" in stdout:
        return "FastForward"
    else:
        return "git: other unknown status (cant parse)"


def pull_repos_for_project(project, use_gut=True):
    config = Config(".")
    config.from_yamlfile(f"neahtta/configs/{project}.config.yaml")
    repos = [d.repo for d in config.dict_entries() if d.repo]
    statuses = dict.fromkeys(repos)

    if not use_gut:
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            tasks = {}
            seen_repo_paths = set()
            for repo in repos:
                repo_path = GUTROOT / "giellalt" / repo
                if repo_path in seen_repo_paths:
                    continue
                seen_repo_paths.add(repo_path)
                future = executor.submit(git_pull, repo_path)
                tasks[future] = repo

            for task in concurrent.futures.as_completed(tasks):
                repo = tasks[task]
                try:
                    result = task.result()
                except Exception as e:
                    statuses[repo] = f"error: {e}"
                    print(repo, "errored:", e)
                else:
                    statuses[repo] = result
    else:
        repos_regex = f"({'|'.join(repos)})"
        cmd = f"{GUT_BINARY} --format=json pull -o giellalt -r {repos_regex}"

        proc = subprocess.run(split_cmd(cmd), capture_output=True, text=True)
        if proc.returncode != 0:
            print(colored("failed", "red"))
            sys.exit(f"Fatal: Error running command: {cmd}\nstderr: {proc.stderr}")

        try:
            parsed_output = json.loads(proc.stdout)
        except json.decoder.JSONDecodeError:
            print(colored("failed", "red"))
            sys.exit(
                f"Fatal: Could not parse json output of gut.\n"
                f"command: {cmd}\n===== stdout =====\n{proc.stdout}"
            )

        for repo in parsed_output:
            statuses[repo["repo"]] = repo["status"]

    return statuses


def do_update(project, no_gut=False):
    print(f"** Checking for dictionary updates for '{project}'...")

    statuses = pull_repos_for_project(project, use_gut=not no_gut)

    n_errors = 0
    n_updated = 0

    for name, status in statuses.items():
        if status == "Nothing":
            print(name, colored("no updates", "green"))
        elif status == "FastForward":
            n_updated += 1
            print(name, colored("updated (fast forward)", "green"))
        elif status == "Normal":
            n_updated += 1
            print(name, colored("updated (merged)", "green"))
        elif status == "SkipConflict" or status == "WithConflict":
            n_errors += 1
            print(name, colored("conflict", "red"))
        else:
            print(name, colored("unknown status!", "red"), f"({status})")

    if n_errors > 0:
        msg = (
            "** Some repositories had conflicts or errors (for some reason)! "
            "Check and fix them manually before compiling new dictionaries."
        )
        print(colored(msg, "red"))
    elif all(status == "Nothing" for status in statuses.values()):
        print(colored("** All up to date", "green"))
    elif n_updated > 0:
        print(colored("** New updates pulled", "green"))
        print(
            "Hint: To update the live site, remember to compile and restart.\n"
            f"nds compile {project}\n"
            f"nds restart {project}"
        )


def update_dicts(project, no_gut=False):
    """Use `gut` to pull all giellalt/dict-* dictionaries for this project."""

    projects = list(available_projects()) if project == "all" else [project]
    for project in projects:
        do_update(project, no_gut)


def run_dev_server(project, trace=False, port=5000):
    print(f"Running development server for {project}")
    os.environ["NDS_CONFIG"] = f"neahtta/configs/{project}.config.yaml"
    if trace:
        os.environ["NDS_TRACE"] = "1"

    from neahtta.neahtta import app

    app.caching_enabled = True
    app.production = False
    app.run(debug=True, port=port, use_reloader=True)


def _find_in_repo(path, org="giellalt"):
    # First try to find it in gut
    gut_path = Path(GUTROOT) / org / path
    if gut_path.exists():
        return gut_path

    # not found under gut, try in $GTLANGS/
    # but remember, $GTLANGS is the same as GUTROOT/giellalt, so ignore org
    try:
        GTLANGS = Path(os.environ["GTLANGS"])
    except KeyError as e:
        msg = (
            f"{path} not found under gut, and when trying to look under "
            "$GTLANGS, $GTLANGS was not set."
        )
        raise FileNotFoundError(msg) from e

    path = Path(GTLANGS) / path

    if path.exists():
        return path

    raise FileNotFoundError(f"{path} not found under gut, nor under $GTLANGS/")


def add_stem():
    """Run add_stemtype2xml.py to add stem type to the sme-nob dict."""
    script_path = _find_in_repo("giella-core/dicts/scripts/add_stemtype2xml.py")

    smi_propernouns = _find_in_repo("shared-smi/src/fst/stems/smi-propernouns.lexc")

    def stemtypes_txt_path(lexc):
        return _find_in_repo(f"dict-sme-nob/scripts/{lexc}_stemtypes.txt")

    for lexc in "nouns", "adjectives", "verbs", "prop":
        cmd = ["python", str(script_path), lexc, str(stemtypes_txt_path(lexc))]
        if lexc != "prop":
            cmd.append("neahtta/dicts/sme-nob.xml")
            cmd.append(
                str(_find_in_repo(f"lang-sme/src/fst/morphology/stems/{lexc}.lexc"))
            )
        else:
            cmd.append(str(stemtypes_txt_path(lexc)))
            cmd.append("neahtta/dicts/sme-nob.xml")
            cmd.append(
                str(
                    _find_in_repo(
                        "lang-sme/src/fst/morphology/stems/sme-propernouns.lexc"
                    )
                )
            )
            cmd.append(smi_propernouns)

        proc = subprocess.run(cmd)

        if proc.returncode != 0:
            print(
                colored(
                    f"** Adding stem type for {lexc} to xml failed, aborting", "red"
                )
            )
            return
        else:
            print(colored(f"** Added stem type for {lexc} to xml", "green"))

        # this happens on every iteration of the loop, but that's how
        # the original code had it
        shutil.copy2("neahtta/dicts/sme-nob.xml.stem.xml", "neahtta/dicts/sme-nob.xml")


def strings_compile(project=None):
    """Run pybabel to compile translation strings found in .po files in the
    translations/ folder to .mo files."""
    if project is not None:
        config = Config(".")
        config.from_yamlfile(f"neahtta/configs/{project}.config.yaml")
        locales = config.yaml["ApplicationSettings"].get("locales_available", [])
        for locale in locales:
            cmd = ["pybabel", "compile", "-d", "neahtta/translations", "-l", locale]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                print("** Compilation", colored("failed", "red"))
                print(proc.stderr)
                return
            print("** Compilation", colored("succeeded", "green"))
    else:
        cmd = ["pybabel", "compile", "-d", "neahtta/translations"]
        print("Running:", *cmd)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            print("")
            print(proc.stdout)
            print(proc.stderr)
        else:
            if "babel.core.UnknownLocaleError" in proc.stderr:
                error_lines = [
                    L
                    for L in proc.stderr.splitlines()
                    if "babel.core.UnknownLocaleError" in L
                ]
                print("** String compilation", colored("failed", "red"))
                print("".join(error_lines))
                print()
                print("hint: Either...")
                print("(1) rerun the command with the project name, i.e.")
                print("    nds strings compile -l PROJECT")
                print("...or...")
                print("(2) Troubleshoot missing locale. (See Troubleshooting doc)")


def strings_extract():
    """Extract all the translation strings to the template and *.po files."""
    print("** Extract strings...")
    cmd = [
        "pybabel",
        "extract",
        "-F",
        "neahtta/babel.cfg",
        "-k",
        "gettext",
        "-o",
        "neahtta/translations/messages.pot",
        ".",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        print("** Extration", colored("failed", "red"))
        print(proc.stderr)
        return

    print("** Extraction ok, updating files...")
    cmd = [
        "pybabel",
        "update",
        "-i",
        "neahtta/translations/messages.pot",
        "-d",
        "neahtta/translations",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("** Update", colored("failed", "red"))
        print(proc.stderr)
        return

    print(colored("** Update ok. You may now check in or translate.", "green"))


def strings_update():
    """Update strings. This function does nothing now. In the old code, it
    did 'git pull', followed by 'nds strings compile'."""
    print(
        "strings_update(): kept for backwards-compliance, but this does "
        "nothing here now.\nThe old code did two things:\ngit pull\nnds "
        "strings compile\nThis is simple enough to do by hand."
    )


def check_fst_files(app):
    # Previously in file configtesters.py
    try:
        fsts = app.config.yaml["Morphology"]
    except KeyError:
        print("WARNING: No top-level key 'Morphology' found in config")
        print("This project has no FST support")
        return

    items = list(fsts.items())

    if not items:
        print(
            "Warning: Top-level mapping 'Morphology' in config contains no languages!"
        )
        return

    for lang, obj in items:
        keys = [("file", "FST file"), ("inverse_file", "Inverse FST file")]
        for key, desc in keys:
            try:
                path = Path("".join(obj[key]))
            except KeyError:
                print(f"Error in config file: Missing key 'file' in Morphology->{lang}")
                continue

            try:
                stat = path.stat()
            except FileNotFoundError:
                print(f"{lang}: {desc}", colored("MISSING", "red"), str(path))
            else:
                print(f"{lang}: {desc}", colored("FOUND", "green"), str(path))
                print(f"UPDATED: {datetime.fromtimestamp(stat.st_mtime)}")


def test_configuration(project):
    """Tries to create the app to see that it works, and runs an existance
    check on the fst files belonging to the project."""
    from neahtta import application

    os.environ["NDS_CONFIG"] = f"neahtta/configs/{project}.config.yaml"

    # this does a lot of the tests
    app = application.create_app()

    # then we do the FST existance checks
    check_fst_files(app)


def image_build(docker, tag):
    cmd = "docker" if docker else "podman"
    os.system(f"{cmd} build -t {tag} -f Dockerfile")


def image_upload(target):
    if target == "gtlab":
        image_upload_gtdict()
    elif target == "azlab":
        image_upload_azlab()


def image_upload_gtdict():
    from getpass import getuser

    if getuser() != "anders":
        print("`whoami` not 'anders', abort. (TODO make it work for others)")
    os.system("scp nds.tar.gz gtdict.uit.no:/home/anders/nds.tar.gz")


def image_upload_azlab():
    # TODO if we get auth failure, tell user to
    # `podman login gtlabcontainerregistry.azurecr.io`, and find
    # username/password in the portal, under "access keys"
    os.system(
        "podman tag neahttadigisanit gtlabcontainerregistry.azurecr.io/neahttadigisanit"
    )
    os.system("podman push gtlabcontainerregistry.azurecr.io/neahttadigisanit")


def image_run_command(project, port=5000, docker=False):
    """Get the command that will run the image."""
    from neahtta.config import Config, MorphologyEntry

    config = Config(".")
    host_config_path = Path(f"neahtta/configs/{project}.config.yaml").resolve()

    # this validates, and also checks existence of files (except dictionaries!)
    config.from_yamlfile(host_config_path)

    langmodels_mounts = []
    for lang, conf_obj in config.yaml["Morphology"].items():
        entry = MorphologyEntry.from_config_dict(lang, conf_obj)
        langmodels_mounts.append(f"-v {entry.file}:{entry.file}")
        if entry.ifile is not None:
            langmodels_mounts.append(f"-v {entry.ifile}:{entry.ifile}")

    cwd = os.getcwd()

    dicts_mounts = []
    missing_dicts = []

    for (_from, _to), path in config.dictionaries.items():
        outside = os.path.join(cwd, "neahtta", path)
        if not os.path.exists(outside):
            missing_dicts.append(outside)

        inside = os.path.join("/nds/neahtta/", path)
        dicts_mounts.append(f"-v {outside}:{inside}")

    if missing_dicts:
        print("Error: Missing dictionaries on the host system, cannot run image")
        print()
        print("Hint: Maybe try to compile dictionaries, using this command:")
        print(f"  nds compile {project}")
        print()
        for missing_dict in missing_dicts:
            print(f"missing: {missing_dict}")
        sys.exit(2)

    langmodels_mounts = " ".join(langmodels_mounts)
    dicts_mounts = " ".join(dicts_mounts)
    inner_config_path = f"/nds/neahtta/{project}.config.yaml"
    config_mount = f"-v {host_config_path}:{inner_config_path}"

    # sanit with sme,SoMe,nob uses 380MB, so 0.5G would be enough for that;
    # but many with full config will use more. maybe set 1Gi in the bicep
    # file for the container.
    # memlimit = "-m 0.5g"

    cmd = "podman" if not docker else "docker"
    cmd_line = (
        f"{cmd} run --rm "
        f"-p {port}:5000 "
        # set the env var which specifies the config file
        f"-e NDS_CONFIG=/nds/neahtta/configs/{project}.config.yaml "
        # memory limit
        # f" {memlimit} "
        # mount in the configuration file
        f" {config_mount} "
        # mount in the compiled dictionaries
        f" {dicts_mounts} "
        # mount in the language models -- read the config file for project
        # to determine where to mount it inside?
        f" {langmodels_mounts} "
        "neahttadigisanit"
    )
    return cmd_line


def image_run(project, port=5000, docker=False):
    cmd = image_run_command(project, port, docker)
    os.system(cmd)


def image_export():
    print("Exporting image, this takes a minute...")
    cmd = "podman save neahttadigisanit:latest | gzip -c > nds.tar.gz"
    print(cmd)
    os.system(cmd)


def image_import():
    print("importing podman image in nds.tar.gz...")
    cmd = "gzip -dc nds.tar.gz | podman load"
    print(cmd)
    os.system(cmd)


def _restart_systemd_service(project):
    print(f"Restarting systemd service 'nds-{project}'...", end="", flush=True)
    proc = subprocess.run(["sudo", "systemctl", "restart", f"nds-{project}"])
    if proc.returncode == 0:
        print(colored("done", "green"))
    else:
        print(colored("failed", "red"))


def restart(project):
    if HOSTNAME != PROD_HOSTNAME and HOSTNAME != PROD_HOSTNAME_02:
        sys.exit(f"On host {HOSTNAME}, which is not a server, nothing was done.")

    if project == "all":
        for project in available_projects():
            _restart_systemd_service(project)
    else:
        _restart_systemd_service(project)


def e2e_run(project=None):
    if project == "all":
        raise NotImplementedError("running e2e tests for all not implemented")

    print(f"Running e2e tests using playwright for project: {project}")
    config = f"e2e/playwright.{project}.config.js"
    cmd = f"pnpm exec playwright test --config={config}"
    subprocess.run(split_cmd(cmd))


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        title="top-level commands",
        dest="cmd",
        metavar="COMMAND",
    )

    available_projects_and_all = ["all", *available_projects()]

    # command: ls
    list_parser = subparsers.add_parser(
        "list-projects",
        aliases=["ls"],
        # help is text that will be shown on `nds --help`,
        # description is for `nds ls --help`
        help="list projects (-i also shows inactive. -d also shows dicts)",
        description=(
            "list projects (-i also shows inactive. -d also shows " "dictionaries)"
        ),
    )
    list_parser.add_argument(
        "project",
        nargs="?",
        default="all",
    )
    list_parser.add_argument(
        "-i",
        "--include-inactive",
        action="store_true",
        help="Also show projects that has a <project>.config.yaml.in file",
    )
    list_parser.add_argument(
        "-d",
        "--include-dicts",
        action="store_true",
        help="Also show the dictionaries belonging to each project",
    )
    list_parser.set_defaults(func=list_projects)

    restart_parser = subparsers.add_parser(
        "restart",
        aliases=["restart-service"],
        # help is text that will be shown on `nds --help`,
        # description is for `nds restart --help`
        help="Restart the production server for a project (only on server!)",
        description="Restart the server for a project (only on gtdict.uit.no)",
    )
    restart_parser.add_argument(
        "project",
        help=(
            "The project. Must be one from the list, or 'all' to restart all "
            "registered systemd services. The list includes only "
            "the ones which has an existing configuration file "
            "<configs/PROJECT.config.yaml>"
        ),
        choices=available_projects_and_all,
    )
    restart_parser.set_defaults(func=restart)

    # command: update
    update_parser = subparsers.add_parser(
        UPDATE_DICTS_ALIASES[0],
        aliases=UPDATE_DICTS_ALIASES[1:],
        description=update_dicts.__doc__,
        help=update_dicts.__doc__,
    )
    update_parser.add_argument(
        "project",
        metavar="PROJECT",
        choices=available_projects_and_all,
        help=(
            "The project whose dictionaries should be updated, or 'all' "
            "to update all dictionaries. Run `nds ls` to see the list of "
            "project names."
        ),
    )
    update_parser.add_argument(
        "--no-gut",
        action="store_true",
        help="Do NOT use gut when pulling git repositories, instead use git",
    )
    update_parser.set_defaults(func=update_dicts)

    # command: compile
    compile_parser = subparsers.add_parser(
        COMPILE_DICTS_ALIASES[0],
        aliases=COMPILE_DICTS_ALIASES[1:],
        help="Compile dictionaries for a project",
        description=compile_dicts.__doc__,
    )
    compile_parser.add_argument(
        "project",
        metavar="PROJECT",
        choices=["all", *available_projects()],
        help="The project to compile dictionaries for. Run `nds ls` "
        "to see the list of project names.",
    )
    compile_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help=(
            "Always recreate the dictionaries (without this, dictionaries "
            "will only be re-created if sources are newer than the "
            "current dictionary file)."
        ),
    )
    compile_parser.set_defaults(func=compile_dicts)

    # command: autoupdate
    autoupdate_parser = subparsers.add_parser(
        "autoupdate",
        description=(
            "Automatically update dictionaries of all instances, and compile "
            "and restart the ones that had updates."
        ),
        help="Auto update and compile all dicts",
    )
    autoupdate_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help=("force compile new dictionaries, even if there weren't any updates"),
    )
    autoupdate_parser.set_defaults(func=autoupdate)

    # command: dev
    dev_parser = subparsers.add_parser(
        "dev",
        description="Run development server locally for a project",
        help="Run development server",
    )
    dev_parser.add_argument(
        "project",
        metavar="PROJECT",
        choices=available_projects(),
        help=(
            "Which project to run the development sever for. Requires that "
            "the associated configuration file <configs/PROJECT.config.yaml> "
            "exists, and is properly configured. You can copy the template "
            "file <configs/PROJECT.config.yaml.in> if it exists, or another "
            "existing configuration file, if the configuration file template "
            "does not exist."
        ),
    )
    dev_parser.add_argument(
        "-t",
        "--trace",
        action="store_true",
        help=(
            "Enable tracing for *very* detailed call graph tracing while "
            "running the dev server. It is very verbose, and slows it down "
            "a lot!"
        ),
    )
    dev_parser.add_argument(
        "-p",
        "--port",
        default=5000,
        help=("run the development server on a custom port (default 5000)"),
    )
    dev_parser.set_defaults(func=run_dev_server)

    # command: test-configuration
    test_configuration_parser = subparsers.add_parser(
        "test",
        aliases=["test-config", "test-configuration"],
        help="Test a project",
        description=test_configuration.__doc__,
    )
    test_configuration_parser.add_argument(
        "project",
        metavar="PROJECT",
        choices=available_projects(),
        help="The project to test. Run `nds ls` list project names.",
    )
    test_configuration_parser.set_defaults(func=test_configuration)

    # command: add-stem
    addstem_parser = subparsers.add_parser(
        "add-stem",
        help="Add stem information to smenob",
        description="Adds stem information to the sme-nob dictionary",
    )
    addstem_parser.set_defaults(func=add_stem)

    # subcommand: strings
    strings_subparser = subparsers.add_parser(
        "strings",
        help="subcommands related to translated strings",
        description="Subcommands related to translated strings",
    )
    strings_parser = strings_subparser.add_subparsers(
        title="translation strings commands",
        dest="cmd",
    )

    # command: strings compile
    strings_compile_parser = strings_parser.add_parser(
        "compile",
        help="Compile .po files to .mo files in the translations/ folder",
        description=strings_compile.__doc__,
    )
    strings_compile_parser.add_argument(
        "project",
        nargs="?",
    )
    strings_compile_parser.set_defaults(func=strings_compile)

    # command: strings extract
    strings_extract_parser = strings_parser.add_parser(
        "extract",
        help="extract translation strings to template- and *.po files",
        description=strings_extract.__doc__,
    )
    strings_extract_parser.set_defaults(func=strings_extract)

    # command: strings update
    strings_extract_parser = strings_parser.add_parser(
        "update",
        help="update strings (removed. it's just git pull && nds strings compile)",
        description=strings_update.__doc__,
    )
    strings_extract_parser.set_defaults(func=strings_update)

    # command: image   (docker/podman image commands)
    image_subparser = subparsers.add_parser(
        "image",
        help="docker/podman image subcommands",
        description="Subcommands related to docker/podman images.",
    )
    image_parser = image_subparser.add_subparsers(
        title="image commands",
        dest="cmd",
    )

    # command: image build
    image_build_parser = image_parser.add_parser(
        "build",
        description="Build the podman (or docker) image of Neahttadigisanit",
        help="Build docker/podman image of Neahttadigisanit",
    )
    image_build_parser.add_argument(
        "--docker",
        action="store_true",
        help="use docker instead of podman",
    )
    image_build_parser.add_argument(
        "-t",
        "--tag",
        default="neahttadigisanit",
        help='set a custom tag (default is "neahttadigisanit")',
    )
    image_build_parser.set_defaults(func=image_build)

    # command: image run
    image_run_parser = image_parser.add_parser(
        "run",
        help="Run the built neahttadigisanit image",
        description="Run the built podman/docker image of neahttadigisanit",
    )
    image_run_parser.add_argument(
        "project",
        metavar="PROJECT",
        choices=available_projects(),
        help="The project config to run inside the image. Run `nds ls` list "
        "project names.",
    )
    image_run_parser.add_argument(
        "-p",
        "--port",
        type=int,  # could check that value is in [1025, 65535]
        default=5000,
        help="The port to bind to on the outside of container",
    )
    image_run_parser.add_argument(
        "--docker",
        action="store_true",
        help="use docker instead of podman",
    )
    image_run_parser.set_defaults(func=image_run)

    # command: image export
    image_export_parser = image_parser.add_parser(
        "export",
        help="export the podman image to a file called nds.tar.gz",
    )
    image_export_parser.set_defaults(func=image_export)

    # command: image import
    image_import_parser = image_parser.add_parser(
        "import",
        help="import the image in nds.tar.gz to podman",
        description=(
            "uses `podman load` to load in the saved image stored in " "nds.tar.gz"
        ),
    )
    image_import_parser.set_defaults(func=image_import)

    # command: image upload
    image_upload_parser = image_parser.add_parser(
        "upload",
        help="upload the image to a container registry, or gtdict",
        description=(
            "Upload the built image to either gtdict, or azure lab. "
            "When uploading to gtdict, a simple `scp` will copy the .tar file "
            "to the server. When uploading to the azure lab container "
            "registry, the normal podman mechanics are used to do the upload."
        ),
    )
    image_upload_parser.add_argument(
        "target",
        help="where to upload the image to",
        choices=["gtdict", "azlab"],
    )
    image_upload_parser.set_defaults(func=image_upload)

    # subcommand: e2e
    e2e_parser = subparsers.add_parser(
        "e2e",
        help="subcommands related to running e2e tests",
        description="Subcommands related to running e2e tests",
    )
    e2e_parser.add_argument(
        "project",
        nargs="?",
        choices=["all", *available_projects()],
        help="which project to run e2e tests for. 'all' runs all",
    )
    e2e_parser.set_defaults(func=e2e_run)

    args = parser.parse_args()

    if args.cmd is None:
        parser.print_usage()
        sys.exit()

    namespace = vars(args)

    func = namespace["func"]
    cmd = namespace["cmd"]
    del namespace["func"]
    del namespace["cmd"]
    return cmd, func, namespace


def main():
    cmd, fn, parameters = parse_args()

    fn(**parameters)


if __name__ == "__main__":
    sys.exit(main())
