from flask import Blueprint

blueprint = Blueprint("views", __name__, template_folder="templates")

from .context_processors import *
from .autocomplete import *
from .reader import *
from .locale import *
from .main import *
from .hooks import *
from .search import *
from .routes import *
