import os

from flask import Flask

from . import db
from . import index, setting, spending, report, backup_data, graphReport

UPLOAD_STATEMENT_FOLDER = 'temp/uploads/statement'
PRELOAD_FOLDER = 'temp/preload'
PRESET_FILE_NAME = 'transaction_preset.csv'
ALLOWED_EXTENSIONS = {'pdf'}


def create_app(test_config=None):
    # Create and configure the application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'finTrack.sqlite'),
        UPLOAD_STATEMENT_FOLDER=UPLOAD_STATEMENT_FOLDER,
        PRELOAD_FOLDER=PRELOAD_FOLDER,
        PRESET_FILE_NAME=PRESET_FILE_NAME,
    )
    # print(os.environ.get("SECRET_EMAILP"))
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    db.init_app(app)
    app.register_blueprint(index.bp)
    app.add_url_rule('/', endpoint='index')
    app.register_blueprint(setting.bp)
    app.register_blueprint(spending.bp)
    app.register_blueprint(report.bp)
    app.register_blueprint(backup_data.bp)
    app.register_blueprint(graphReport.bp)

    return app
