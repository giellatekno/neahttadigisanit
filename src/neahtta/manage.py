# manage.py
# -*- encoding:utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from termcolor import colored
from flask import Flask
from flaskext.actions import Manager
from neahtta import app

manager = Manager(app, default_server_actions=True)


@manager.register('compilemessages')
def compilemessages(app):
    """ TODO: pybabel compile -d translations
    """

    def action():
        print(""" You might be looking for this ...
            - pybabel compile -d translations
        """)
        return False

    return action


@manager.register('makemessages')
def hello(app):
    def action():
        """ You might be looking for this ...
            - pybabel extract -F babel.cfg -k lazy_gettext -o translations/messages.pot .
            - pybabel update -i translations/messages.pot -d translations
        """
        return False

    return action


if __name__ == "__main__":
    app.caching_enabled = True
    manager.run()
