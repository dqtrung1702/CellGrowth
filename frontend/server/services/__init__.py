from flask import Flask, Blueprint
from importlib import import_module
from base import csrf_protect, attach_csrf_cookie, inject_menu_flags
import pkgutil
from pathlib import Path

def create_app(config):
  app = Flask(
    __name__, 
    static_folder="../../client/static", 
    # static_url_path="", 
    template_folder= "../../client/template")
  app.config.from_object(config)
  app.before_request(csrf_protect)
  app.after_request(attach_csrf_cookie)
  app.context_processor(inject_menu_flags)
  register_blueprints(app)
  return app

def register_blueprints(app):
  pkg = __name__  # typically "services"
  pkg_path = Path(__file__).parent
  for _, name, ispkg in pkgutil.iter_modules([str(pkg_path)]):
    if name.startswith('_') or name.endswith('_test'):
      continue
    module = import_module(f'{pkg}.{name}')
    _register_blueprints_from_module(app, module)
    if ispkg:
      # ensure package submodules are loaded via its __init__
      continue

def _register_blueprints_from_module(app, module):
  for attr in dir(module):
    obj = getattr(module, attr)
    if isinstance(obj, Blueprint):
      app.register_blueprint(obj)
