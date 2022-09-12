from __future__ import absolute_import
from . import blueprint
from flask import current_app, g, request, session
from i18n.utils import iso_filter


@blueprint.before_request
def set_pair_request_globals():
    """ Set global language pair infos.
    """
    _from = request.view_args.get('_from')
    _to = request.view_args.get('_to')

    if '_from' in request.view_args and '_to' in request.view_args:
        g._from = request.view_args.get('_from')
        g._to = request.view_args.get('_to')
    elif 'from_language' in request.view_args and 'to_language' in request.view_args:
        g._from = request.view_args.get('from_language')
        g._to = request.view_args.get('to_language')
    else:
        if str(request.url_rule) == '/':
            g._from, g._to = current_app.config.default_language_pair
            _from, _to = current_app.config.default_language_pair

    if hasattr(g, '_to'):
        g.ui_lang = iso_filter(session.get('locale', g._to))
    else:
        g.ui_lang = iso_filter(session.get('locale'))

    current_pair_settings, orig_pair_opts = current_app.config.resolve_original_pair(
        _from, _to)
    g.current_pair_settings = current_pair_settings

    orig = orig_pair_opts.get('orig_pair')
    if orig != ():
        g.orig_from, g.orig_to = orig
    else:
        g.orig_from, g.orig_to = _from, _to
