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
        print """ You might be looking for this ...
            - pybabel compile -d translations
        """
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

@manager.register('chk-fst-paths')
def hello(app):

    def get_dates(_file):
        import os.path, time
        return time.ctime(os.path.getctime(_file))

    def action():
        fsts = app.config.yaml.get('Morphology').iteritems()
        print ''
        print 'Checking config files and whether they exist...'
        for k, v in fsts:
            file_path = ''.join(v.get('file'))
            i_file_path = ''.join(v.get('inverse_file'))
            file_exists   = 'MISSING: '
            i_file_exists = 'MISSING: '
            try:
                with open(file_path):
                    file_exists = 'FOUND:   '
                    dates       = 'UPDATED: %s' % get_dates(file_path)
            except IOError:
                pass
            try:
                with open(i_file_path):
                    i_file_exists = 'FOUND:   '
                    i_dates       = 'UPDATED: %s' % get_dates(i_file_path)
            except IOError:
                pass

            print "%s:" % k
            print "  " + file_exists + file_path
            print "  " + dates
            print ''
            print "  " + i_file_exists + i_file_path
            print "  " + i_dates
            print ''
            print ''

        return False
    return action

if __name__ == "__main__":
    app.caching_enabled = True
    manager.run()

