import json
import logging
from datetime import datetime

from aiohttp import web
from aiohttp_jinja2 import render_template
from aiohttp_session import get_session, Session

from app.tree.models import Tree, GenderEnum
from constant import DATETIME_FORMAT, DATE_FORMAT


async def user_tree(request: web.Request, tree: Tree, session: Session):
    message_data = []
    messages = await tree.query.where(tree.user_id == session['user_id']).gino.all()
    for tree_object in messages:
        message_data.append({
            'id': tree_object.id,
            'dt_created': tree_object.dt_created.strftime(DATETIME_FORMAT),
            'dt_updated': tree_object.dt_updated.strftime(DATETIME_FORMAT),
            'name': tree_object.name,
            'description': tree_object.description,
            'pids': tree_object.pids,
            'mid': tree_object.mid,
            'fid': tree_object.fid,
            'gender': tree_object.gender.value,
            'birth_date': tree_object.birth_date.strftime(DATE_FORMAT),
            'photo_url': tree_object.photo_url
        })
    context = {'nodes': message_data}
    response = render_template('family_tree_with_js.html', request, context)
    return response


async def delete_node(request: web.Request, tree: Tree, session: Session, logger: logging.Logger):
    try:
        result = await tree.delete.where(Tree.id == int(request.query['id'])).gino.status()
        logger.info(f'User {session["profile_info"]["email"]} deleted tree id {request.query["id"]}')
        return web.Response(status=200, text=result[0])
    except ValueError as e:
        logger.error(
            f'Attempting to delete node, user {session["profile_info"]["email"]}. Wrong node id {request.query["id"]}')
        return web.Response(status=400, text=str(e))


async def update_node(request: web.Request, tree: Tree):
    new_data = await request.json(loads=json.loads)
    status = await tree.update.values(
        name=new_data['name'],
        birth_date=datetime.strptime(new_data['birth_date'], '%Y-%m-%d').date(),
        description=new_data['description']).where(Tree.id == new_data['id']).gino.status()
    return web.Response(status=200, text=status[0])


async def error(request: web.Request, session: Session):
    if not session:
        context = {'error_text': 'Please LogIn'}
        response = render_template('error.html', request, context)
        return response
    if error_text := session.get('error', None):
        context = {'error_text': error_text}
        response = render_template('error.html', request, context)
        return response
    else:
        raise web.HTTPFound('/')


async def get_node(request: web.Request, tree: Tree, session: Session):
    tree_record_list = await tree.query.where(tree.user_id == session['user_id']).gino.all()
    mother_list = []
    father_list = []
    user_list_free_pid = []
    for tree_record in tree_record_list:
        if tree_record.gender == GenderEnum.male:
            father_list.append(({tree_record.id}, f'{tree_record.name} {tree_record.birth_date}'))
        else:
            mother_list.append(({tree_record.id}, f'{tree_record.name} {tree_record.birth_date}'))
        if not tree_record.pids:
            user_list_free_pid.append(({tree_record.id}, f'{tree_record.name} {tree_record.birth_date}'))
    context = {'mother_list': mother_list, 'father_list': father_list, 'user_list_free_pid': user_list_free_pid}
    response = render_template('add_new_node.html', request, context)
    return response


async def add_node(request: web.Request, tree: Tree, session: Session, logger: logging.Logger):
    body_list = (await request.read()).replace(b'%', b'\\x').decode('unicode_escape').encode(
        'raw_unicode_escape').decode('utf-8').split('&')
    body_dict = {string[0:string.find('=')]: string[string.find('=') + 1:] for string in body_list}
    if body_dict['pid']:
        partner_list = await request.app['db'].tree.query.where(Tree.id == int(body_dict['pid'])).gino.all()
        for partner in partner_list:
            if partner.gender.value == body_dict['gender']:
                (await get_session(request))['error'] = "You can`t create relationship between same gender"
                raise web.HTTPFound('/error')
    new_tree = await tree.create(
        birth_date=datetime.strptime(body_dict['birth_date'], '%d.%m.%Y').date(),
        name=body_dict['full_name'].replace('+', ' '),
        description=body_dict['description'].replace('+', ' '),
        pids=[int(body_dict['pid'])] if body_dict['pid'] != '' else None,
        mid=int(body_dict['mid']) if body_dict['mid'] != '' else None,
        fid=int(body_dict['fid']) if body_dict['fid'] != '' else None,
        gender=GenderEnum.male if body_dict['gender'] == 'male' else GenderEnum.female,
        dt_created=datetime.now(),
        dt_updated=datetime.now(),
        user_id=session['user_id'],
        photo_url=body_dict['photo_url']
    )
    logger.info(f'User {session["profile_info"]["email"]} create new node with id {new_tree.id}')
    if new_tree.pids:
        partner_tree = await tree.get(*new_tree.pids)
        await partner_tree.update(pids=[new_tree.id]).apply()
    return web.HTTPFound('/')


async def login(request: web.Request):
    return render_template('login.html', request, None)
