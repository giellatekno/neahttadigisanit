# Neahttadigisánit

A dictionary website that searches the XML dictionary sources, as well as
doing morphological analysis on the input, to find more results. This lets
us find conjugated word forms which are not in the dictionary, plus more.

We use the issue tracker at
[github.com/giellatekno/neahttadigisanit/issues](https://github.com/giellatekno/neahttadigisanit/issues),
but see also the `TODOs` file.

This readme contains programmer-oriented documentation, see
[neahttadigisanit](https://giellalt.github.io/dicts/neahttadigisanit.html)
for a more general overview, and lingustic and maintainer-oriented
documentation.

# Installing and developing

## Prerequisites

### python

Python version 3.9 is required. It may or may not work with older or newer
versions, but 3.9 is what we target, and have tested for. You can use
[pyenv](https://github.com/pyenv/pyenv) or similar tools to install different python versions on your
system. If you have `pyenv` installed, it will respect the `.python-version`
file (which is just literally `3.9`), and issuing `python` in the root folder
will start python 3.9. If not, then make sure that you substitute any `python`
command with your command that runs python version 3.9.

### node.js and npm

Any version should work. Make sure that the `node` and `npm` commands are
available.

### gut

[gut](https://github.com/divvun/gut) is used internally by the management
script, to update dictionaries. It must be installed on the system.

### language models files ("fsts")

Refer to [Giellatekno documentation](https://giellalt.github.io) on
installation of language models.
You can use precompiled language models from apertium nightly, or compile them
yourself. Just remember to place them according to how you set up the
`Morphology` section in a project's configuration file.

### dictionaries

Make sure that the dictionaries that a configuration depends on are installed
and updated, through gut. Which dictionaries a specific "project" uses, can
be seen with `nds ls -di`.


## Installing

Create a virtual environment, and activate it

    python -m venv .venv
    . .venv/bin/activate

There are a few javascript dependencies, used for building and bundling.
Install them with `npm` (from the `neahtta/` directory):

    cd neahtta/
    npm install

### Extras

Long story short, there are two ways of doing the installation, depending
on if you're on the server, or developing locally.

For the server, use

    (venv) pip install ".[server]"

While for developing locally, use

    (venv) pip install -e ".[dev,pyhfst]"

Explanation:

The `-e` flag installs "editable". The `[dev,pyhfst]` indicates installation
of two optional dependencies. `dev` installs a code formatter, while `pyhfst`
will install the python bindings to libhfst. On the server, the python bindings
cannot be installed per now (there is no built distribution for our system).
On the server, `gunicorn` is needed to run in production.


## Development server

Run the development server with

    nds dev <project>

Run it with the call stack tracer with

    nds dev <project> --trace

The output from the tracer can help you orient yourself in the code, and can
be helpful when debugging. Note that it slows the dev server down a good bit,
and the output is **very** verbose.


## e2e testing with Playwright

First make sure you have Playwright installed in the project. Using `pnpm`
this should be as simple as

```bash
pnpm i
```

in the root `neahtta/` directory.

To run the end-to-end (_e2e_) tests, run

    nds e2e <project>

The command will run the dev server for that instance automatically.

Note that as the command is essentially a wrapper around 

    `pnpm exec playwright test --config={config}"`

... it is required to have pnpm installed - at least as of right now.


## Production Server

On `gtdict.uit.no`, nginx is the web server. It proxies to Gunicorn, which is
the WSGI server for Flask. The setup is very similar to the example in the
[Gunicorn docs][1]. There is one Gunicorn instance for every project, so by
issuing a `ps aux` on the server, will show them: `nds-sanit`, `nds-sanat`, etc.

  [1]: https://docs.gunicorn.org/en/latest/deploy.html#systemd


### Systemd service

Each Gunicorn instance on the server is managed by a systemd service unit,
located in `/etc/systemd/system/nds-xxx.service`. To add a new project, edit the
template file `nds-.service`, and copy it to `/etc/systemd/system/nds-xxx.service`.
Most of the changes needed to be done are quite self-explanatory. Change the
name in `Description`, change the `Environment` to point to the yaml config
file, etc.

When it comes to the `ExecStart` line, take notice of which port you bind to,
`nginx` has to be configured to have a server or a path that `proxy_pass`-es
to this port.


### autoupdate timer

On the server, dictionaries are updated hourly. A service called
`autoupdate-nds` is set to by a corresponding *timer* to run hourly, through
systemd. The service runs `nds autoupdate`, which pulls dictionaries from
github, compiles new ones, and restarts instances if new dictionaries were
compiled.


## Alternative production setup: docker/podman image

Build a docker/podman image of Neahttadigisánit using

    nds image build

Run it using

    nds image run <project>

By default it listens to port `5000`. It is configurable with the `-p`
argument to `nds image run`. All the required files (_config file_,
_compiled dictionaries_, and _language model files ("fsts")_) are mapped in
from the host system transparently when running the `nds image run` command.
Basically, if `nds dev <project>` works, then `nds image run <project>`
should also work.

The image conceptually just contains the code to run the app (although in
practice some things do currently get copied in) - so it needs a few files
mounted into the container, namely

 - The configuration file
 - The built dictionaries (in `dicts/` that the configuration file references)
 - The language model files that the configuration file references

Append `--help` to any _image_ command to get more help about it.

Use `nds image build` to build an image. Run `nds image build --help` for
additional help and to see available arguments.


### Azure setup

(WIP) how i imagine the setup on Azure:

    resource group: neahttadigisanit
      storage account:
        file shares:
          - nds-configs
            (where we store config files)
      container app:
        image: gtcontainerregistry.azurecr.io/neahttadigisanit
        config files: mounted in from File Share "nds-configs"
        dictionaries: compiled dictionaries mounted in from File Share "xxx?"
        language model files ("fsts"): mounted in from File Share "langmodels"

But for now, since the image contains configurations as well as compiled
dictionaries, it's easier for the container to just use them directly.
The only thing that I need to map in (because they are not copied in),
are the langmodels.

The `bicep` file only allows a directory to be mapped in. A full file share
is mapped in under some given directory path. I will need to map in the
langmodels file share in its entirety....


## Module overview

For Python-module specific documentation, see the docstrings available in the
individual Python files. A short overview follows:

 * `neahtta.py` - initialization of Flask app, endpoints.
 * `config.py` - wrapper for config files in `config/`
 * `configs/PROJ.config.yaml` - active configuration for PROJ
 * `configs/PROJ.config.yaml.in` - inactive template configuration for PROJ
 * `configs/language_names.py` - ISO names and 2-char -> 3-char definitions
 * `configs/language_specific_rules` - Overriden code, templates, template filters, morphology and lexical overrides, etc for languages/projects.
 * `views/` - Defining routes in Flask, mapping them to defined handlers. This includes "data-routes" that the site uses. For example for autocompletions.
 * `translations/` - i18n/i10n/localization details and .po files.
 * `nds_lexicon/` - XML Dictionary (Lexicon) functionality
 * `nds_lexicon/lexicon.py` - Parsing of XML dictionary files. Code for overriden lexical functionality per project/language/etc.
 * `nds_lexicon/trie.py` - Trie implementation.
 * `morphology/` - FST parsing, lemmatization modules
 * `morpholex/` - Thing that ties these two together
 * `static/` - js, css, img, etc.
 * `templates/` - jinja2 templates for endpoints. Can be overriden per project, and also per language pair in `configs/language_specific_rules/templates`
 * `dicts/` - Compiled XML dictionaries

## XML format

See https://giellalt.github.io/dicts/dictionarywork.html


## Memory usage notes

(Temporary notes regarding memory usage when using 'pyhfst' instead of
'hfst' format in config files. The former loads in the `.hfstol` files in
memory on startup, and so uses quite a bit more memory than the what the
'hfst' version does. But we gain ~150ms (at least) of latency reduction on
queries.)

```
sanit (pyhfst, only sme+some+nob): `pmap` total: 1273648K
sanit (hfst, only sme+some+nob): `pmap` total: 883796K
diff: 389852K (~= 380 M)

file sizes:
sme/analyser-dict-gt-desc.hfstol: 30M
sme/generator-dict-gt-norm.hfstol: 29M
nob/analyser-dict-gt-desc-mobile.hfstol: 6.7M
nob/generator-dict-gt-norm.hfstol: 6.3M

sme is used twice: in SoMe also. So:
30+30 + 29+29 + 6.7+6.3 = 131.0 M
... quite a lot lower than the 380 reported by pmap
even if we x2 131, that's 262 (and still not 380).
(but the two processes share memory (I think)).

sanit (pyhfst sme, rest hfst): `pmap` total: 1052432K
the files are 59M, diff from only hfst: 
1052432K - 883796K = 168636 (=~ 164 MB)
```
