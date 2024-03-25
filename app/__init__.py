from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

#db = SQLAlchemy()
scheduler = APScheduler()

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #db.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    from app.task import grab_providers

    #grab_providers()

    return app