from cerberus import Validator
from datetime import datetime
from utils import get_body_or_bad_request, forbidden, bad_request, ok, get_current_user_permission
import numbers
import json
from schemas import PATCH_ADMIN_SETTINGS_SCHEMA
from db import lambda_handler as db_handler


def patch_site_settings_values(**kwargs):
    body = kwargs.get('body')
    email = kwargs.get('email')

    settings = {
        'site_visibility': body.get('site_visibility', ''),
        'title': body.get('title', ''),
        'fontsize': body.get('fontsize', ''),
        'coloraccent': body.get('coloraccent', ''),
        'isdarkmode': body.get('isdarkmode', ''),
        'description': body.get('description', ''),
        'copyright': body.get('copyright', ''),
        'websiteurl': body.get('websiteurl', ''),
        'brandmail': body.get('brandmail', ''),
        'brandlogourl': body.get('brandlogourl', ''),
        'faviconurl': body.get('faviconurl', ''),
        'appiconurl': body.get('appiconurl', '')
    }

    schema_validation = Validator(PATCH_ADMIN_SETTINGS_SCHEMA)

    remove_empty_values_of_dict(settings)

    resp = None
    if schema_validation.validate(settings):

        query = dynamic_update_query(
            settings, 'settings.site_settings', '', email)

        print(query)

        msg = {
            'body': {
                'action': 'run',
                'queries': [query]
            }
        }

        method, result = db_handler(msg)

        print(result)

        if method == 'ok':
            resp = settings
    else:
        return bad_request(schema_validation.errors)
    return ok(resp)


def patch_settings_from_event(**kwargs):

    event = kwargs.get('event')
    user_id = kwargs.get('user_id')
    query_string = kwargs.get('query_string')
    email = kwargs.get('email')

    print(event)

    body_or_bad_request = get_body_or_bad_request(event)
    if body_or_bad_request['error']:
        return body_or_bad_request['response']
    body = body_or_bad_request['response']
    print(body)

    user_permission = get_current_user_permission(
        user_id, query_string['permission'])

    print(user_permission)

    if not user_permission['authorized']:
        return forbidden()

    return patch_site_settings_values(body=body, email=email)


def dynamic_update_query(body, table, condition, upd_email):
    values = []
    for key in body:
        if isinstance(body[key], numbers.Number):
            values.append(f"{key} = {str(body[key])}")
        else:
            values.append(f"{key} = '{str(body[key])}'")
    values = values + upd_tms_and_upd_by(upd_email)
    values = ', '.join(values)
    if condition:
        where_stmt = f"WHERE {condition}"
    else:
        where_stmt = f"WHERE 1=1"
    update_query = f"UPDATE {table} SET {values} {where_stmt}".strip()
    return update_query


def remove_empty_values_of_dict(dictionary):
    """
    Clean empty values of the payload so we don't delete values.
    """
    key_to_remove = []
    for key in dictionary:
        if dictionary[key] == '':
            key_to_remove.append(key)
    for key in key_to_remove:
        dictionary.pop(key)


def upd_tms_and_upd_by(upd_email):
    now = datetime.utcnow()
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    query = [f"last_modified = '{now}'", f"modified_by = '{upd_email}'"]
    return query
