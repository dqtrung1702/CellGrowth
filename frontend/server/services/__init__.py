from flask import Flask
from importlib import import_module
from base import csrf_protect, attach_csrf_cookie, inject_menu_flags

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
  lstModule = ['authentication','home_','user','role','permission','dataset','person']
  pkg = __name__  # typically "services"
  for item in lstModule:
    module = import_module(f'{pkg}.{item}')
    app.register_blueprint(getattr(module, item))
    # app.secret_key = 'nhập từ khóa tùy thích’
