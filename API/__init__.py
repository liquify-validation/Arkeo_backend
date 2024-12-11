import logging
import os
from flask import Flask, jsonify, redirect
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from passlib.hash import pbkdf2_sha256
from flaskTemplate import template as flaskTemplate
from flaskTemplate import swagger_config as swaggerConfig
from flask_cors import CORS, cross_origin
from flasgger import Swagger
from flask_migrate import Migrate
from API.providers import ProviderBlueprint
from API.providers.task import grab_providers
from API.contracts.task import grab_contracts
from API.contracts import ContractBlueprint
from API.network.task import grab_network_stats, grab_nonce_counter
from API.network import NetworkBlueprint
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from dotenv import load_dotenv

load_dotenv()


from config import config


def create_flask_app(db, db_url=None):
    app = Flask(__name__)
    # setup_oauth(app)
    swagger = Swagger(app, template=flaskTemplate, config=swaggerConfig)
    CORS(app)

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    logger.info('Flask app starting...')

    app.config.from_object(config.Config)
    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    with app.app_context():
        scheduler = BackgroundScheduler()
        scheduler.start()
        scheduler.add_job(func=grab_providers, trigger=IntervalTrigger(minutes=5), args=[app])
        scheduler.add_job(func=grab_contracts, trigger=IntervalTrigger(minutes=1), args=[app])
        scheduler.add_job(func=grab_network_stats, trigger=IntervalTrigger(minutes=1), args=[app])
        scheduler.add_job(func=grab_nonce_counter, trigger=CronTrigger(minute=0), args=[app])

    app.register_blueprint(ProviderBlueprint, url_prefix='/providers')
    app.register_blueprint(ContractBlueprint, url_prefix='/contracts')
    app.register_blueprint(NetworkBlueprint, url_prefix='/network')

    return app