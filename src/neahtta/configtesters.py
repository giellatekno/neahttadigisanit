# configtesters.py
# -*- encoding:utf-8 -*-

from termcolor import colored
from application import create_app
import os.path, time
from six import iteritems


def _get_dates(_file):
    return time.ctime(os.path.getctime(_file))

def chk_fst_paths():
    app = create_app()
    fsts = iteritems(app.config.yaml.get('Morphology'))
    print('')
    print('Checking config files and whether they exist...')
    missing_fst = False
    for k, v in fsts:
        file_path = ''.join(v.get('file'))
        i_file_path = ''.join(v.get('inverse_file'))
        file_exists = colored('MISSING: ', 'red')
        i_file_exists = colored('MISSING: ', 'red')
        dates = 'UPDATED: ?'
        i_dates = 'UPDATED: ?'
        try:
            with open(file_path):
                file_exists = colored('FOUND:   ', 'green')
                dates = 'UPDATED: %s' % _get_dates(file_path)
        except IOError:
            missing_fst = True
        try:
            with open(i_file_path):
                i_file_exists = colored('FOUND:   ', 'green')
                i_dates = 'UPDATED: %s' % _get_dates(i_file_path)
        except IOError:
            missing_fst = True

        print("%s:" % k)
        print("  " + file_exists + file_path)
        print("  " + dates)
        print('')
        print("  " + i_file_exists + i_file_path)
        print("  " + i_dates)
        print('')
        print('')

    if missing_fst:
        print(colored("Some FSTs were not found. See above.", "red"))
