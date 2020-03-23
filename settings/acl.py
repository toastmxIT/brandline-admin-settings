from cerberus import Validator

from db import lambda_handler as db_handler
from schemas import ACL_MANAGEMENT_SCHEMA

ACL_MANAGEMENT_VALIDATOR = Validator(ACL_MANAGEMENT_SCHEMA)

ALLOWED_ACTIONS = ['check-user-permissions']


def get_permissions_by_user_id(user_id):
    sql = f'''
        select pt.name
        from roles.permission_type as pt
        inner join roles.permission as p on p.permission_type_id = pt.id
        inner join roles.permission_role as pr on pr.permission_id = p.id
        inner join roles.role as r on r.id = pr.role_id
        inner join users.users as u on u.role_id = r.id
        where u.id = '{user_id}'
    '''

    msg = {
        'body': {
            'action': 'run',
            'queries': [sql]
        }
    }

    method, response = db_handler(msg)

    if method == 'ok':
        print(response)
        return response[0]
    else:
        return None


def get_role_name_by_user_id(user_id):
    return f'''
        select r.name
        from roles.role as r
        inner join users.users as u on u.role_id = r.id
        where u.id = '{user_id}'
    '''


def lambda_handler(event):
    body = event["body"] if event["body"] else None

    if not body:
        return 'bad_request', {'message': 'Event request does not contain body object'}

    if 'action' not in body:
        return 'bad_request', {'message': 'Body does not contain \'action\' key'}

    if body["action"] not in ALLOWED_ACTIONS:
        return 'bad_request', {
            'message': 'Body does not contain a valid action. Valid actions are: ' + ','.join(ALLOWED_ACTIONS)}

    if body["action"] == 'check-user-permissions':
        if ACL_MANAGEMENT_VALIDATOR.validate(body):
            # get the permission of the user
            user_permission = get_permissions_by_user_id(body["user_id"])
            if body["permission"] in user_permission:

                return 'ok', {'authorized': 'True'}
            else:
                # else, return bad request
                return 'forbidden', {}
        else:
            return 'bad_request', ACL_MANAGEMENT_VALIDATOR.errors
