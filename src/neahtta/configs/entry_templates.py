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

"""

import os, sys
import yaml

from lxml import etree

__all__ = ['TemplateConfig']

# A collection for tracking compiled templates. This may provide more
# complexity than necessary: need to check, 
parsed_template_cache = {}

# TODO: read from user defined file elsewhere

class TemplateConfig(object):
    """ A class for providing directory-based paradigm definitions.
    This class reads and parses the configs for the sets of languages
    available, and provides a general method for resolving the proper
    paradigm from dictionary entry nodes and morphological analyses. """

    def __init__(self, app=None, debug=False, cache=True):
        self.debug = debug
        self._app = app
        self.cache = cache

        self.template_dir = os.path.join( os.getcwd()
                                        , 'configs/language_specific_rules/templates/'
                                        )
        self.instance = app.config.short_name
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
        from jinja2 import FileSystemLoader
        # TODO: possible to config filesystem loader to reread
        # templates? If so, ensure the template cache is refreshed.

        self.jinja_env.loader = FileSystemLoader(self.template_loader_dirs)

        def process_template_set(ts):
            _ts = {}
            for k, path in ts.iteritems():
                _ts[k] = self.read_template_file(path)
            return _ts

        # Process self.default_templates
        self.default_templates = process_template_set(self.default_templates)

        # Process self.project_templates
        self.project_templates = process_template_set(self.project_templates)

        # Process self.language_templates
        _l_ts = self.language_templates.copy()

        for l, temps in _l_ts.iteritems():
            _l_ts[l] = process_template_set(temps)

        self.language_templates = _l_ts

        return

    def get_template(self, language, template):
        """ .. py:function:: get_paradigm(language, node, analyses)

        Render a paradigm if one exists for language.

        :param str language: The 3-character ISO for the language.
        :param lxml node: The lxml element for the <e /> node selected from a lookup
        :param list analyses: A list containing Lemma objects from a lookup.

        :return unicode: Plaintext string containing the paradigm to be generated, including
        any context provided.

        """

        return self.language_templates[language][template]

    def render_template(self, language, template, **extra_kwargs):
        """ Do the actual rendering. This is run for each entry in a lookup.

        Here we apply some things to the context that the user probably
        needs: access to lookup parameters, individual templates, and
        already rendered templates.

        Then at the end, a fully rendered result is returned.

        """

        tpl = self.get_template(language, template)

        context = {}
        context['template_root'] = os.path.dirname(tpl.path) + '/'

        # Add templates to the context
        context['templates'] = dict(
            (k.replace('.template', ''), v)
            for k, v in self.language_templates[language].iteritems()
            if k.endswith('.template')
        )

        context['rendered_templates'] = {}

        try:
            lookup_params = extra_kwargs.pop('lookup_parameters')
        except:
            lookup_params = {}

        context['lookup_parameters'] = lookup_params

        context.update(extra_kwargs)

        # Now render the templates for each entry. If there's an error,
        # then we consider it a failure for everything and raise an
        # exception.

        rendered = {}
        for k, t in self.language_templates[language].iteritems():
            if k != template and k.endswith('.template'):
                try:
                    rendered[k.replace('.template', '')] = t.render(**context)
                except Exception, e:
                    msg = e.message
                    msg += " in template <%s>" % t.path.partition('language_specific_rules')[2]
                    raise e.__class__(msg)

        context['rendered_templates'] = rendered

        # Return the rendered main template.
        return tpl.render(**context)

    def read_templates_directory(self):
        """ .. py:method:: read_paradigm_directory()

        Read through the paradigm directory, and read .paradigm files

        In running contexts, this expects a Flask app instance to be
        passed. For testing purposes, None may be passed.

        Constructs self.default_templates, self.project_templates,
        self.language_templates

        """
        from collections import defaultdict
        from functools import partial

        if self.debug:
            print >> sys.stderr, "* Reading template directory."

        # Path relative to working directory
        _path = self.template_dir

        self.language_templates = {}
        self.template_loader_dirs = [
            os.path.join(os.getcwd(), 'templates/'),
        ]

        def _dirs(p):
            """ Is the path a directory? (TODO: can use different walker) """
            return not p.endswith('.template') and \
                   not p.endswith('.macros') and \
                   not p.startswith('.')

        def _templates(p):
            return p.endswith('.template') or p.endswith('.macros')

        def join_path(p, f):
            return (f, os.path.join(p, f))

        def scan_path_dirs(_p):
            return filter(_dirs, os.listdir(_p))

        def template_dict_for_path(p):
            _join_path = partial(join_path, p)
            return dict( map( _join_path
                            , filter( _templates
                                    , os.listdir(p)
                                    )
                            )
                       )

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
            proj_directories = [ p for p in proj_directories
                                 if p == self.instance ]

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

        # NB, it may be tempting to rewrite this as a recursive
        # strategy, but there's no need yet.

        for project in proj_directories:
            project_templates = root_templates.copy()

            _proj_path = os.path.join( _path
                                     , project
                                     )

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

                _lang_proj_path = os.path.join( os.path.join( _path, project)
                                              , lang
                                              )

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
        """ Here we print the handy tree of overridden things
        """
        print
        print 'templates/ '
        for t in self.default_templates.keys():
            print '   ⌘ ' + t

        print 
        print '  %s/ ' % self.instance

        for k, f in self.project_templates.iteritems():
            if f.path not in [p.path for p in self.default_templates.values()]:
                print u'    ⌘ ' + k
            else:
                print u'      ' + k
        print

        for lang, temps in self.language_templates.iteritems():
            print u'      %s/' % lang

            for k, f in temps.iteritems():
                if f.path not in [p.path for p in self.project_templates.values()]:
                    print u'      ⌘ ' + k
                else:
                    print u'        ' + k

            print

        print ' ⌘ - overridden here.'
        print
        print

    def read_template_file(self, path):
        if path not in parsed_template_cache:
            with open(path, 'r') as F:
                _raw = F.read().decode('utf-8')
            return self.parse_template_string(_raw, path)
        else:
            return parsed_template_cache.get(path)

    def _template_parse_error_msg(self, exception, path):
        print
        print '--'
        print >> sys.stderr, "Error parsing template at <%s>" % path
        print >> sys.stderr, exception
        print '--'
        print

    def parse_template_string(self, template_string, path):
        parsed_condition = False

        try:
            parsed_template = self.jinja_env.from_string(template_string)
            parsed_template.path = path
        except Exception, e:
            self._template_parse_error_msg(e, path)
            sys.exit()

        return parsed_template

if __name__ == "__main__":
    # TODO: make a test of this instead.
    from application import create_app

    app = create_app()
    app.debug = True

    with app.app_context():
        lookup = app.morpholexicon.lookup('mannat', source_lang='sme', target_lang='nob')
        pc = TemplateConfig(app)
        for lexicon, analyses in lookup:
            print '--'
            print pc.render_template('sme', 'entry.template',
                                     lexicon_entry=lexicon,
                                     analyses=analyses, _from='sme',
                                     _to='nob')
            print '--'
            print

    # for l in app.config.languages.keys():
    #     print l + ':'
    #     print pc.render_template(l, 'entry.template')
    #     print

