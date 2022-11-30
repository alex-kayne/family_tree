from app.auth import views as auth_views
from app.tree import views as tree_view
from constant import OAUTH2CALLBACK_PATH


def setup_routes(app):
    app.router.add_get('/', tree_view.user_tree)
    app.router.add_get('/user_tree_js',
                       tree_view.tree_js)  # retrieve js for tree. TODO replace with link on static file
    app.router.add_get('/add_new_node', tree_view.get_node)
    app.router.add_post('/add_new_node', tree_view.add_node)
    app.router.add_get('/error', tree_view.error)
    app.router.add_delete('/delete_node', tree_view.delete_node)
    app.router.add_post('/update_node', tree_view.update_node)
    # Authorization
    app.router.add_get('/auth', auth_views.authorize)
    app.router.add_get(f'/{OAUTH2CALLBACK_PATH}', auth_views.oauth2callback)
    app.router.add_get('/login', tree_view.login)
    app.router.add_get('/logout', auth_views.revoke)


def setup_auth(app):
    auth_views.authorize.login_method = True
    tree_view.login.auth_free = True
    app['refresh_access_token'] = auth_views.refresh_access_token
