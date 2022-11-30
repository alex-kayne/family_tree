import logging
from datetime import datetime as dt

from aiohttp import web
from aiohttp_session import Session, get_session, new_session
from gino import Gino

import constant
from app.tree.models import Tree, User


class SessionCheck:

    @staticmethod
    async def is_authed_and_is_refreshed_token(request, session):
        is_refreshed = False
        if not session:
            session = await get_session(request)
        if 'credentials' in session:
            if dt.strptime(session['credentials']['expiry'], constant.DATETIME_FORMAT) < dt.utcnow():
                is_refreshed = await request.app['refresh_access_token'](session)
        return True if session.get('is_authed') else False, is_refreshed

    @web.middleware
    async def middleware(self, request, handler):
        params = {}
        session = None
        for arg_name, annotation in handler.__annotations__.items():
            if annotation is web.Request:
                params[arg_name] = request
            elif annotation is Gino:
                params[arg_name] = request.app['db'].db
            elif annotation is Tree:
                params[arg_name] = request.app['db'].tree
            elif annotation is User:
                params[arg_name] = request.app['db'].user
            elif annotation is logging.Logger:
                params[arg_name] = request.app['logger']
            elif annotation is Session:
                if getattr(handler, 'login_method', False):
                    params[arg_name] = await new_session(request)
                    params[arg_name]['is_authed'] = True
                else:
                    params[arg_name] = await get_session(request)
                session = params[arg_name]
            else:
                pass
        if getattr(handler, 'auth_free', False):
            return await handler(**params)
        is_authed, is_refreshed_token = await SessionCheck.is_authed_and_is_refreshed_token(request, session)
        if not is_authed:
            return web.HTTPFound('/login')
        return await handler(**params)
