import json
from cerberus import Validator
from schemas import GET_ADMIN_SETTINGS_URL_SCHEMA
from utils import bad_request, ok, get_enviroment_var, internal_server_error, forbidden, get_cognito_email
from db import lambda_handler as db_handler
from acl import lambda_handler as acl_handler
from http import HTTPStatus

ADMIN_SETTINGS_URL_VALIDATOR = Validator(GET_ADMIN_SETTINGS_URL_SCHEMA)


def get_site_settings_values():
    sql = f'''
        select 	site_visibility,
                title,
                fontsize,
                selfurl,
                coloraccent,
                isdarkmode,
                description,
                copyright,
                websiteurl,
                brandmail,
                brandlogourl,
                faviconurl,
                appiconurl
        from settings.site_settings
    '''

    msg = {
        'body': {
            'action': 'run',
            'queries': [sql]
        }
    }

    response = db_handler(msg)

    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        body = json.loads(body[0])
        return ok(body[0])
    else:
        return internal_server_error()


def get_user_id_by_email(email):
    sql = f'''
        select u.id
        from users.users as u
        where u.email = '{email}'
    '''

    msg = {
        'body': {
            'action': 'run',
            'queries': [sql]
        }
    }

    print(msg)

    response = db_handler(msg)
    print(type(response))
    print(response)

    if response['statusCode'] == HTTPStatus.OK:
        body = json.loads(response['body'])
        body = json.loads(body[0])
        return body[0]['id']
    else:
        return None


def get_current_user_permission(user_id, permission):
    msg = {
        'body': {
            'action': 'check-user-permissions',
            'user_id': user_id,
            'permission': permission
        }
    }

    response = acl_handler(msg)

    print(response)

    if response['statusCode'] == HTTPStatus.OK:
        return response['body']
    else:
        return None


def lambda_handler(event, context):

    if event['httpMethod'] == 'GET':
        query_string = event['queryStringParameters'] if event['queryStringParameters'] else None

        if not query_string:
            return bad_request({'message': 'The event does not contain queryStringParameters'})

        if ADMIN_SETTINGS_URL_VALIDATOR.validate(query_string):
            # get the user
            email = get_cognito_email(event)
            print(email)
            user_id = get_user_id_by_email(email)

            print(user_id)

            if not user_id:
                return forbidden()

            # get the permission of the user
            user_permission = json.loads(get_current_user_permission(user_id, query_string['permission']))

            print(user_permission)

            if user_permission['authorized'] == 'True':
                # if yes, then get data
                return get_site_settings_values()
            else:
                # else, return bad request
                return forbidden()
        else:
            return bad_request(ADMIN_SETTINGS_URL_VALIDATOR.errors)
