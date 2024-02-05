from flask import redirect, request, session


def set_locale(iso):
    from flask_babel import refresh

    session["locale"] = iso

    try:
        del session["force_locale"]
    except KeyError:
        pass

    # Refresh the localization infos, and send the user back whence they
    # came.
    refresh()
    ref = request.referrer
    if ref is not None:
        return redirect(request.referrer)
    else:
        return redirect("/")
