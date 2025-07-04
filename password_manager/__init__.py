import os
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'pwd_mgr.sqlite')  
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import sqlite_db
    sqlite_db.init_app(app)

    from . import manager, auth
    app.register_blueprint(manager.bp, url_prefix='/manager')
    app.register_blueprint(auth.bp)

    @app.route('/hello')
    def hello():
        return 'Hello, World'
    
    return app
