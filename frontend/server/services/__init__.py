from flask import Flask,Blueprint
from importlib import import_module

def create_app(config):
  app = Flask(
    __name__, 
    static_folder="../../client/static", 
    # static_url_path="", 
    template_folder= "../../client/template")
  app.config.from_object(config)
  register_blueprints(app)
  return app

def register_blueprints(app):
  lstModule = ['authentication','home_','user','role','permission']
  for item in lstModule:
    module = import_module('services.{}'.format(item))
    app.register_blueprint(getattr(module, item))
    # app.secret_key = 'nhập từ khóa tùy thích’
