import os

from flask import Flask
from flask_mail import Mail, Message
from . import db, emailService
from . import index, setting, spending, report, backup_data, graphReport
from flask_apscheduler import APScheduler
import time

mail = Mail()


def create_app(test_config=None):
    # Create and configure the application
    app = Flask(__name__, instance_relative_config=True)
    app.config['DEBUG'] = True
    global mail
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'finTrack.sqlite'),
        MAIL_SERVER='smtp.qq.com',
        MAIL_PORT=465,
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=True,
        MAIL_DEBUG=app.debug,
        MAIL_USERNAME='342049327@qq.com',
        MAIL_PASSWORD='FamilyHappy1989',
        MAIL_DEFAULT_SENDER=None,
        MAIL_MAX_EMAILS=None,
        MAIL_SUPPRESS_SEND=app.testing,
        MAIL_ASCII_ATTACHMENTS=False,
    )
    #print(os.environ.get("SECRET_EMAILP"))
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

    # emailService.scheduleEmail()
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    mail.init_app(app)

    @app.route('/run-tasks')
    def run_tasks():
        """
        for i in range(10):
            app.apscheduler.add_job(func=scheduled_task, trigger='date', args=[i], id='j' + str(i))
        """
        app.apscheduler.add_job(func=emailTest, trigger='date', args=[0], id='email')

        return 'Scheduled several long running tasks.', 200

    def scheduled_task(task_id):
        for i in range(10):
            time.sleep(1)
            print('Task {} running iteration {}'.format(task_id, i))

    def emailTest(task_id):
        with mail.connect() as conn:
            msg = Message("Hello, task id is {}".format(task_id),
                          sender="342049327@qq.com",
                          recipients=["xumenglove@icloud.com"])
            conn.send(msg)

    return app