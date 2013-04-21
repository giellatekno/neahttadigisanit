from flask import ( request
                  , redirect
                  , session
                  )

from . import blueprint

@blueprint.route('/locale/<iso>/', methods=['GET'])
def set_locale(iso):
    from flaskext.babel import refresh

    session['locale'] = iso
    # Refresh the localization infos, and send the user back whence they
    # came.
    refresh()
    ref = request.referrer
    if ref is not None:
        return redirect(request.referrer)
    else:
        return redirect('/')

