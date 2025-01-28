# -*- encoding: utf-8 -*-
"""
So far:
 * Reads directory structure
 * manages overriding parent templates
 * importing macros seems to work
 * can reference other pre-renedered templates in process.
 * works in both main view and detail

TODO: this destroys entry sorting and mg sorting

TODO: how do local vs. global macros work exactly?

TODO: template for rendering remainder of analysis with no entry.

TODO: local CSS files

TODO: reprocess template directories on save doesn't seem to work,
      figure this out somehow

TODO: once we're actually only using these, can do a lot of code cleanup
      of views, soon we will be doing more with less.

TODO:  mobile width - detail - paradigm disappears, was problematic on
    old templates, doublecheck here.

TODO: generated context accessible with new templates? is the way it's
      done now ideal?

TODO: sme pregenerated forms don't really work without sme.py

"""
import os
import sys
from jinja2 import TemplateSyntaxError
from jinja2.exceptions import TemplateNotFound

__all__ = ["TemplateConfig", "LanguageNotFound"]


def cwd(x):
    return os.path.join(os.path.dirname(__file__), x)


class LanguageNotFound(Exception):
    """Language not found for this project."""


# TODO: read from user defined file elsewhere
# TODO: see following, consider constructing a template loader for all
# this stuff, will help to implement live reloading of project stuff.

#   https://github.com/pallets/jinja/blob/master/jinja2/loaders.py


class TemplateConfig:
    """A class for providing directory-based paradigm definitions.
    This class reads and parses the configs for the sets of languages
    paradigm from dictionary entry nodes and morphological analyses."""

    errorable_templates = [
        "analyses.template",
        "entry.template",
        "paradigm.template",
    ]
    # Templates in this list will not be rendered on every other page load
    no_subview_rendering = [
        "variant_search.template",
        "detail_search_form.template",
    ]

    def __init__(self, app=None, debug=False, cache=True):
        self.debug = debug
        self._app = app
        self.cache = cache

        self.template_dir = os.path.join(
            app.config.language_specific_rules_path, "templates/"
        )

        self.instance = app.config.short_name
        self.render_template_errors = app.config.render_template_errors
        self.languages_available = app.config.languages.keys()

        # Use a plain jinja environment if none exists.
        if self._app is None:
            from jinja2 import Environment

            self.jinja_env = Environment()
        else:
            self.jinja_env = self._app.jinja_env

        self.read_templates_directory()

        self.process_template_paths()

        if self.debug:
            self.print_debug_tree()

    def process_template_paths(self):
        from jinja2 import ChoiceLoader, FileSystemLoader

        # A choice loader for the deepest potential directory first,
        # so when the template loader is used to select a template
        # (generally only when rendering full page templates), the
        # intended option will appear.

        # NB: if this becomes insufficient, PrefixLoader might be good.
        # Can bind options to a prefix, so, sanit/blah.template would
        # resolve to the right thing. Could thus make a loader on top of
        # that to try with a prefix, and then return the unprefixed
        # variant

        reversed_priority = self.template_loader_dirs[::-1]

        self.jinja_env.loader = ChoiceLoader(
            [FileSystemLoader(cwd("templates"))]
            + [FileSystemLoader(p) for p in reversed_priority]
        )

        def process_template_set(ts):
            """Replace paths with parsed template contents."""
            replaced = {}
            for template_name, path in ts.items():
                with open(path) as f:
                    template_contents = f.read()
                try:
                    parsed_template = self.jinja_env.from_string(template_contents)
                except (TemplateSyntaxError, Exception) as e:
                    msg = f"Error in template: {path}"
                    if e.lineno:
                        msg += f" (line {e.lineno})"
                    msg += f"\n{e}"
                    sys.exit(msg)
                parsed_template.path = path
                replaced[template_name] = parsed_template

            return replaced

        # Process self.default_templates
        self.default_templates = process_template_set(self.default_templates)

        # Process self.project_templates
        self.project_templates = process_template_set(self.project_templates)

        # Process self.language_templates
        _l_ts = self.language_templates.copy()

        for L, temps in _l_ts.items():
            _l_ts[L] = process_template_set(temps)

        self.language_templates = _l_ts

    def has_template(self, language, template):
        """Returns a boolean value for the source language iso
        and the template name.
        """
        try:
            self.get_template(language, template)
        except (LanguageNotFound, TemplateNotFound, KeyError):
            return False

        return True

    def has_local_override(self, language, template):
        """Returns a boolean value for the source language iso and the
        template name, but only if the project short name is found in
        the template path (meaning a local override exists).
        """
        try:
            tpl = self.get_template(language, template)
        except (LanguageNotFound, TemplateNotFound, KeyError):
            tpl = False

        # TODO: partition path based on
        # app.config.language/specific_rules
        if tpl:
            _, _, _path = tpl.path.partition("language_specific_rules")
            return self.instance in _path

        return tpl

    def get_template(self, language, template):
        """.. py:function:: get_template(language, template)

        Render a paradigm if one exists for language.

        :param str language: The 3-character ISO for the language.
        :param str template: The template name

        :return Template: Parsed template object
        """

        # TODO: what exception works best if template doesn't exist
        if language not in self.language_templates:
            raise LanguageNotFound(f"Missing language <{language}>")
        if template not in self.language_templates[language]:
            raise TemplateNotFound(f"Missing template <{template}>")
        return self.language_templates[language][template]

    def render_individual_template(self, language, template, **kwargs):
        # Used to render at least
        # search_info.template
        # index_search_form.template
        # notice.template
        # footer.template
        # analyses.template
        # includes.template
        # find_problem.template

        tpl = self.get_template(language, template)

        is_still_renderable = template in self.errorable_templates

        # Add default values
        context = {}

        context.update(**kwargs)

        # Return the rendered main template.
        try:
            rendered = tpl.render(**context)
        except Exception as e:
            if is_still_renderable:
                rendered = self.render_individual_template(
                    language,
                    "template_error.template",
                    **{
                        "exception": e.__class__,
                        "message": repr(e),
                        "render_template_errors": self.render_template_errors,
                        "template_name": tpl.path.partition("language_specific_rules")[
                            2
                        ],
                    },
                )
            else:
                raise e

        return rendered

    def render_template(self, language, template, **kwargs):
        """Do the actual rendering. This is run for each entry in a lookup.

        Here we apply some things to the context that the user probably
        needs: access to lookup parameters, individual templates, and
        already rendered templates.

        Then at the end, a fully rendered result is returned.

        """
        # Seems to only be used to render:
        # entry.template
        # detail_entry.template

        from flask import g

        tpl = self.get_template(language, template)
        is_still_renderable = template in self.errorable_templates
        error_tpl = self.get_template(language, "template_error.template")

        # add default things
        dict_opts = self._app.config.dictionary_options.get((g._from, g._to))

        context = {
            "lexicon_entry": False,
            # Provide access to lexicon options, xpath statements, etc
            "dictionary_options": dict_opts,
            "analyses": [],
            "user_input": False,
            "word_searches": False,
            "errors": False,
            "show_info": False,
            "successful_entry_exists": False,
            "paradigm": [],
        }

        context["template_root"] = os.path.dirname(tpl.path) + "/"

        # Add templates to the context
        context["templates"] = dict(
            (k.replace(".template", ""), v)
            for k, v in self.language_templates[language].items()
            if k.endswith(".template")
        )

        context["rendered_templates"] = {}

        lookup_params = kwargs.pop("lookup_parameters", {})

        context["lookup_parameters"] = lookup_params

        context.update(kwargs)

        # Now render the templates for each entry. If there's an error,
        # then we consider it a failure for everything and raise an
        # exception.

        rendered = {}
        for k, t in self.language_templates[language].items():
            if (
                k != template
                and k.endswith(".template")
                and k not in self.no_subview_rendering
            ):
                try:
                    rendered[k.replace(".template", "")] = t.render(**context)
                except Exception as e:
                    # anders: this makes it hard crash on template errors!
                    raise
                    # DEBUG "e has no attribute message"
                    # msg = e.message
                    msg = (
                        "Error in template <%s>"
                        % t.path.partition("language_specific_rules")[2]
                    )
                    e_context = {
                        "exception": e.__class__,
                        "message": e.__class__(msg),
                        "template_name": t.path.partition("language_specific_rules")[2],
                        "render_template_errors": self.render_template_errors,
                    }

                    if is_still_renderable:
                        rendered[k.replace(".template", "")] = error_tpl.render(
                            **e_context
                        )
                    else:
                        raise e.__class__(msg)

        context["rendered_templates"] = rendered

        # Return the rendered main template.
        return tpl.render(**context)

    def read_templates_directory(self):
        """.. py:method:: read_templates_directory()

        Read through the template directory, and read .template and .macros files

        In running contexts, this expects a Flask app instance to be
        passed. For testing purposes, None may be passed.

        Constructs self.default_templates, self.project_templates,
        self.language_templates
        """
        from functools import partial

        if self.debug:
            print("* Reading template directory.", file=sys.stderr)

        # Path relative to working directory
        _path = self.template_dir

        self.language_templates = {}
        self.template_loader_dirs = [
            # anders: path change
            os.path.join(os.getcwd(), "neahtta/templates/"),
        ]

        def _dirs(p):
            """Is the path a directory? (TODO: can use different walker)"""
            return (
                not p.endswith(".template")
                and not p.endswith(".macros")
                and not p.startswith(".")
            )

        def _templates(p):
            return p.endswith(".template") or p.endswith(".macros")

        def join_path(p, f):
            return (f, os.path.join(p, f))

        def scan_path_dirs(_p):
            return list(filter(_dirs, os.listdir(_p)))

        def template_dict_for_path(p):
            # anders: the dict(list(map(list(filter())))) thing below is
            # a bit difficult to read, so I refactored
            paths = {}
            for filename in os.listdir(p):
                if filename.endswith(".template") or filename.endswith(".macros"):
                    paths[filename] = os.path.join(p, filename)

            _join_path = partial(join_path, p)
            orig_result = dict(
                list(map(_join_path, list(filter(_templates, os.listdir(p)))))
            )

            assert (
                orig_result == paths
            ), "template_dict_for_path: new and old code does the same"
            return paths

        # We only want the ones that exist for this instance.
        proj_directories = scan_path_dirs(_path)

        # This holds the root templates, which we'll copy for each
        # project, and language within that project, and then override
        # with the local files.

        # A dictionary of root templates:
        # {'name.template': '/path/to/name.template'}

        self.template_loader_dirs.append(_path)

        root_templates = template_dict_for_path(_path)
        self.default_templates = root_templates.copy()

        # Find project directories belonging to the instance.
        if self.instance:
            proj_directories = [p for p in proj_directories if p == self.instance]

        # project is not defined in directory structure, so, we just
        # need to copy defaults.
        if self.instance not in proj_directories:
            project_templates = root_templates.copy()
            self.project_templates = project_templates

            for lang in self.languages_available:
                self.language_templates[lang] = project_templates

            # And we're done here.
            return

        # get all the .template files that belong to a project

        for project in proj_directories:
            project_templates = root_templates.copy()
            _proj_path = os.path.join(_path, project)

            # Add the path for the template loader
            self.template_loader_dirs.append(_proj_path)

            # Construct the template path dict for the project
            local_project_templates = template_dict_for_path(_proj_path)

            # Override the default templates with the local changes
            project_templates.update(local_project_templates)
            self.project_templates = project_templates.copy()

            # Now we roughly repeat the process on language directories.
            for lang in scan_path_dirs(_proj_path):
                lang_project_templates = project_templates.copy()

                _lang_proj_path = os.path.join(os.path.join(_path, project), lang)

                # Template loader
                self.template_loader_dirs.append(_lang_proj_path)

                # Construct the dict for the language
                local_lang_project_templates = template_dict_for_path(_lang_proj_path)

                # Override the previous level's templates with the ones
                # found here.
                lang_project_templates.update(local_lang_project_templates)

                # Add to language template paths
                self.language_templates[lang] = lang_project_templates

        # Now populate the default project settings for the languages
        # that are not defined in the directory structure.

        for lang in self.languages_available:
            if lang not in self.language_templates:
                self.language_templates[lang] = self.project_templates.copy()

    def print_debug_tree(self):
        """Here we print the handy tree of overridden things"""
        print()
        print("templates/ ")
        for t in self.default_templates.keys():
            print("   + " + t)

        print()
        print(f"  {self.instance}/ ")
        sys.stdout.flush()

        for k, f in self.project_templates.items():
            if f.path not in [p.path for p in self.default_templates.values()]:
                print("    + " + k)
                sys.stdout.flush()
            else:
                print("      " + k)
                sys.stdout.flush()
        print()
        sys.stdout.flush()

        for lang, temps in self.language_templates.items():
            print(f"      {lang}/")

            for k, f in temps.items():
                if f.path not in [p.path for p in self.project_templates.values()]:
                    print("      + " + k)
                    sys.stdout.flush()
                else:
                    print("        " + k)
                    sys.stdout.flush()

            print()
            sys.stdout.flush()

        print(" + - overridden here.")
        sys.stdout.flush()
        print()
        print()
