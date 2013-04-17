# manage.py
# -*- encoding:utf-8 -*-

from flask import Flask
from flaskext.actions import Manager
from neahtta import app

manager = Manager(app, default_server_actions=True)

@manager.register('compilemessages')
def compilemessages(app):
    """ TODO: pybabel compile -d translations
    """
    def action():
        raise NotImplementedError
    return action
        

@manager.register('makemessages')
def hello(app):
    """ TODO: two steps
        - pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
        - pybabel update -i messages.pot -d translations
    """
    def action():
        # Do actual command stuff here
        raise NotImplementedError
    return action

if __name__ == "__main__":
    app.caching_enabled = True
    manager.run()

