def register_filters(app):

    from flask import render_template
    import urllib as urllib
    from markupsafe import Markup

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e, *args, **kwargs):
        return render_template('500.html', error=e), 500

    @app.template_filter('iso_to_language_own_name')
    def iso_to_language_own_name(_iso):
        from configs.language_names import LOCALISATION_NAMES_BY_LANGUAGE
        return LOCALISATION_NAMES_BY_LANGUAGE.get(_iso, _iso)

    @app.template_filter('iso_to_i18n')
    def append_language_names_i18n(s):
        from configs.language_names import NAMES
        return NAMES.get(s, s)

    @app.template_filter('sneak_in_link')
    def sneak_in_link(s, link_src):
        """ Split a string at the first parenthesis, if the string contains
        any, and wrap the first part in a link; otherwise wrap the whole
        thing in a link.
        """

        target_word, paren, rest = s.partition('(')

        if paren:
            return '<a href="%s">%s</a> (%s' % ( link_src
                                               , target_word
                                               , rest
                                               )
        else:
            return '<a href="%s">%s</a>' % ( link_src
                                           , target_word
                                           )

    @app.template_filter('tagfilter')
    def tagfilter(*args, **kwargs):
        from morphology.utils import tagfilter
        return tagfilter(*args, **kwargs)

    @app.template_filter('xml_lang')
    def xml_lang(nodes, _to):
        return [n for n in nodes if _to in n.xpath('@xml:lang')]

    @app.template_filter('urlencode')
    def urlencode_filter(s):
        if type(s) == 'Markup':
            s = s.unescape()
        s = s.encode('utf8')
        s = urllib.quote_plus(s)
        return Markup(s)


    return app
