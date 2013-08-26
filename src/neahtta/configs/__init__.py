from language_specific_rules import load_overrides
import language_names

from flask import Blueprint

blueprint = Blueprint('configs', __name__, template_folder='templates')
blueprint.load_language_overrides = load_overrides

__all__ = [ 'language_names'
          , 'blueprint'
          ]
