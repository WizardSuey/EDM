from flask import Flask, render_template
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
from flask_ckeditor import CKEditor
import os
import logging

# logger = logging.getLogger(__name__)
# logging.basicConfig(filename='myapp.log', level=logging.INFO)

socketio = SocketIO()
ckeditor = CKEditor()

def create_app(config: str = 'dev'):
    app = Flask(__name__)
    
    if config == 'dev':
        app.config.from_pyfile('config/dev_config.py', silent=True)
        app.config
    elif config == 'test':
        app.config.from_pyfile('config/test_config.py', silent=True)
    elif config == 'prod':
        app.config.from_pyfile('config/prod_config.py', silent=True)
    else:
        raise ValueError(f'Unknown config: {config}')

    from . import databae
    databae.init_app(app)

    socketio.init_app(app)
    ckeditor.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/', endpoint='dashboard.index')

    from . import documents
    app.register_blueprint(documents.bp)

    return app