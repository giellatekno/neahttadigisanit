from __future__ import absolute_import
from __future__ import print_function
import os
import unittest

import neahtta

# TODO: run a test against all sme stuff


class TemplateRenderTest(unittest.TestCase):
    """ Test basic template rendering.
    """

    def setUp(self):
        from entry_templates import TemplateConfig

        _app = neahtta.app
        # Turn on debug to disable SMTP logging
        _app.debug = True
        _app.logger.removeHandler(_app.logger.smtp_handler)

        # Disable caching
        _app.caching_enabled = False
        self.app = _app.test_client()
        self.current_app = _app
        self.template_renderer = TemplateConfig(self.current_app)

    def testRenderSme(self):

        with self.current_app.app_context():
            lookup = self.current_app.morpholexicon.lookup(
                'mannat', source_lang='sme', target_lang='nob')
            # TODO: current_app missing new style template filter
            # extension
            for lexicon, analyses in lookup:
                rendered = self.template_renderer.render_template(
                    'sme',
                    'entry.template',
                    lexicon_entry=lexicon,
                    analyses=analyses,
                    _from='sme',
                    _to='nob')
                print(rendered)
