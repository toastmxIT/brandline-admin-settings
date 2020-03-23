import json
from cerberus import Validator
from schemas import GET_ADMIN_SETTINGS_URL_SCHEMA
from utils import bad_request, ok, internal_server_error, forbidden, get_current_user_permission
from db import lambda_handler as db_handler

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

    method, response = db_handler(msg)

    if method == 'ok':
        response_dict = response[0][1:-1]
        return ok(json.loads(response_dict))
    else:
        return internal_server_error()


def get_settings_from_event(query_string, user_id):

    if ADMIN_SETTINGS_URL_VALIDATOR.validate(query_string):
        # get the permission of the user
        user_permission = get_current_user_permission(
            user_id, query_string['permission'])

        print(user_permission)

        if user_permission['authorized'] == 'True':
            # if yes, then get data
            return get_site_settings_values()
        else:
            # else, return bad request
            return forbidden()
    else:
        return bad_request(ADMIN_SETTINGS_URL_VALIDATOR.errors)
