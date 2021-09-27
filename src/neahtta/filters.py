FLAGS = {}


def file_exists(path):
    try:
        with open(path, 'r'):
            return True
    except:
        return False
    return False


def register_filters(app):

    from flask import render_template, send_from_directory, request
    import urllib as urllib
    from markupsafe import Markup

    @app.route('/robots.txt')
    @app.route('/sitemap.xml')
    def static_from_root():
        return send_from_directory(app.static_folder, request.path[1:])

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e, *args, **kwargs):
        return render_template('500.html', error=e), 500

    @app.template_filter('iso_to_language_own_name')
    def iso_to_language_own_name(_iso):
        from flask import current_app
        from flask import g

        LOCALISATION_NAMES_BY_LANGUAGE = current_app.config.LOCALISATION_NAMES_BY_LANGUAGE
        return LOCALISATION_NAMES_BY_LANGUAGE.get(
            _iso, LOCALISATION_NAMES_BY_LANGUAGE.get(g.orig_from, _iso))

    @app.template_filter('iso_display_relabel')
    def iso_display_relabel(_iso):
        from flask import g
        from flask import current_app
        L = current_app.config.ISO_DISPLAY_RELABELS
        return L.get(_iso, _iso)

    @app.template_filter('iso_has_flag')
    def iso_has_flag(iso):
        import os
        if app.config.menu_flags:
            if iso in FLAGS:
                return FLAGS[iso]
            _path = os.path.join('static/img/flags/', iso + '_20x15.png')
            exists = file_exists(_path)
            FLAGS[iso] = exists
            return FLAGS[iso]
        else:
            return False

    @app.template_filter('filter_pairs_by_source')
    def filter_pairs_by_source(pairs, source):
        for ((_from, _to), data) in pairs:
            if _from == source:
                yield ((_from, _to), data)

    @app.template_filter('filter_pairs_by_target')
    def filter_pairs_by_target(pairs, target):
        for ((_from, _to), data) in pairs:
            if _to == target:
                yield ((_from, _to), data)

    @app.template_filter('is_variant_of')
    def is_variant_of(s, items):
        is_variant = False
        available_variants = sum([
            i.get('input_variants')
            for k, i in items if i.get('input_variants')
        ], [])
        is_variant = any(
            [True for av in available_variants if av.get('short_name') == s])
        return is_variant

    @app.template_filter('iso_to_i18n')
    def append_language_names_i18n(s):
        from flask import g, current_app
        from flask.ext.babel import lazy_gettext
        NAMES = current_app.config.NAMES

        _n = NAMES.get(s, NAMES.get(g.orig_from, s))
        return lazy_gettext(_n)

    @app.template_filter('sneak_in_link')
    def sneak_in_link(s, link_src):
        """ Split a string at the first parenthesis, if the string contains
        any, and wrap the first part in a link; otherwise wrap the whole
        thing in a link.
        """

        target_word, paren, rest = s.partition('(')

        if paren:
            return '<a href="%s">%s</a> (%s' % (link_src, target_word, rest)
        else:
            return '<a href="%s">%s</a>' % (link_src, target_word)

    @app.template_filter('tagfilter')
    def tagfilter(*args, **kwargs):
        from morphology.utils import tagfilter
        return tagfilter(*args, **kwargs)

    @app.template_filter('tagfilter_generation')
    def tagfilter_generation(*args, **kwargs):
        from morphology.utils import tagfilter
        kwargs['generation'] = True
        return tagfilter(*args, **kwargs)

    @app.template_filter('tagfilter_by')
    def tagfilter_by(tag_string, _f, _t, tagset, **kwargs):
        from morphology.utils import tagfilter
        return tagfilter(tag_string, _f, _t, tagset=tagset, **kwargs)

    @app.template_filter('xml_lang')
    def xml_lang(nodes, _to):
        return [n for n in nodes if _to in n.xpath('@xml:lang')]

    @app.template_filter('split_string')
    def split_string(s, delim=' '):
        return s.strip().split(delim)

    @app.template_filter('urlencode')
    def urlencode_filter(s):
        if type(s) == 'Markup':
            s = s.unescape()
        s = s.encode('utf8')
        s = urllib.quote_plus(s)
        return Markup(s)

    @app.template_filter('urlencode_quote')
    def urlencode_filter_quote(s, safe='#&='):
        if type(s) == 'Markup':
            s = s.unescape()
        s = s.encode('utf8')
        s = urllib.quote(s, safe=safe)
        return Markup(s)

    @app.template_filter('unique')
    def unique_filter(s):
        """
        Returns a list of GeneratedForm objects with unique forms
        """
        from morphology.morphology import GeneratedForm
        if isinstance(s[0], GeneratedForm):
            forms_list = []
            return_list = []
            for form_obj in s:
                if form_obj.form in forms_list:
                    continue
                else:
                    forms_list.append(form_obj.form)
                    return_list.append(form_obj)
            return(return_list)
        else:
            return(s)


    return app
