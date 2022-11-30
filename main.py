import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.nacl_storage import NaClCookieStorage
from cryptography import fernet

from app.logger import setup_loger
from app.middleware.gen_middleware import SessionCheck
from app.settings import config, BASE_DIR
from app.store.database.accessor import PostgresAccessor
from app.tree.routes import setup_routes as setup_tree_routes, setup_auth


def session_setup(application):
    setup(application, NaClCookieStorage(fernet.Fernet.generate_key()[0:32], max_age=5400))


def setup_config_and_logger(application):
    application['config'] = config
    application['logger'] = setup_loger()


def setup_external_libraries(application):
    aiohttp_jinja2.setup(
        application,
        loader=jinja2.FileSystemLoader(f'{BASE_DIR}/templates')
    )


def setup_accessor(application):
    application['db'] = PostgresAccessor()
    application['db'].setup(application)


def setup_routes(application):
    setup_tree_routes(application)
    setup_auth(application)


def setup_app(application):
    setup_config_and_logger(application)
    session_setup(application)
    setup_accessor(application)
    setup_external_libraries(application)
    setup_routes(application)


app = web.Application()

if __name__ == '__main__':
    setup_app(app)
    session_check_middleware = SessionCheck()
    app.middlewares.append(session_check_middleware.middleware)
    web.run_app(app, host=config['common']['host'], port=config['common']['port'])
