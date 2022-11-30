import datetime

import aiohttp
import google.oauth2.credentials
import google_auth_oauthlib.flow
from aiohttp import web
from aiohttp_session import Session

from app.tree.models import User
from constant import SCOPES, CLIENT_SECRETS_FILE, OAUTH2CALLBACK_PATH, DATETIME_FORMAT


async def authorize(request: web.Request, session: Session):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = f'http://{request.app["config"]["common"]["host"]}:{request.app["config"]["common"]["port"]}/{OAUTH2CALLBACK_PATH}'
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    session['state'] = state
    return web.HTTPFound(authorization_url)


async def oauth2callback(request: web.Request, session: Session, user: User):
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = f'http://{request.app["config"]["common"]["host"]}:{request.app["config"]["common"]["port"]}/{OAUTH2CALLBACK_PATH}'
    authorization_response = str(request.url).replace('http', 'https', 1)
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    profile_info = flow.authorized_session().get(
        'https://www.googleapis.com/userinfo/v2/me').json()
    session['credentials'] = {'token': credentials.token,
                              'refresh_token': credentials.refresh_token,
                              'client_id': credentials.client_id,
                              'client_secret': credentials.client_secret,
                              'expiry': credentials.expiry.strftime(DATETIME_FORMAT)
                              }
    session['profile_info'] = profile_info
    ex_user = await user.query.where(User.email == profile_info['email']).gino.first()
    if not ex_user:
        ex_user = await user.create(email=profile_info['email'],
                                    full_name=profile_info['name'],
                                    first_name=profile_info['given_name'],
                                    last_name=profile_info['family_name'],
                                    picture=profile_info['picture'])
    session['user_id'] = ex_user.id
    return web.HTTPFound('/')


async def revoke(session: Session):
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])

    async with aiohttp.ClientSession() as client_session:
        async with client_session.post('https://oauth2.googleapis.com/revoke',
                                       params={'token': credentials.token},
                                       headers={'content-type': 'application/x-www-form-urlencoded'}) as resp:
            status_code = resp.status
    if status_code == 200:
        session.invalidate()
        return web.HTTPFound('/login')
    else:
        session['error'] = 'Can not log out, sorry'
        raise web.HTTPFound('/error')


async def refresh_access_token(session: Session):
    params = {
        'client_id': session['credentials'].get('client_id'),
        'client_secret': session['credentials'].get('client_secret'),
        'refresh_token': session['credentials'].get('refresh_token'),
        'grant_type': 'refresh_token'
    }

    async with aiohttp.ClientSession() as client_session:
        async with client_session.post('https://oauth2.googleapis.com/token',
                                       params=params) as resp:
            status = resp.status
            response_dict = await resp.json()

    if status == 200:
        session['credentials'].update({'token': response_dict['token']})
        session['credentials'].update({'expiry': datetime.datetime.utcnow()
                                                 + datetime.timedelta(seconds=response_dict['expires_in'])})
        return True
    return False
