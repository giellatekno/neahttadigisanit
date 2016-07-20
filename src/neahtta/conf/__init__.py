from flask import Blueprint
from confdir import load_overrides

blueprint = Blueprint('configs', __name__, template_folder='templates')
blueprint.load_language_overrides = load_overrides

__all__ = [ 'blueprint' ]

