import json
from cerberus import Validator
from schemas import GET_ADMIN_SETTINGS_URL_SCHEMA
from utils import get_body_or_bad_request, bad_request, ok, get_enviroment_var, internal_server_error, forbidden, get_cognito_email
from boto3 import client as boto3_client

ACL_MANAGEMENT_LAMBDA = '-'.join(
    [get_enviroment_var(pa) for pa in ['ACL_MANAGEMENT_STACK', 'ACL_MANAGEMENT_LAMBDA', 'LAMBDA_ENV']]
)

DB_LAMBDA = '-'.join(
    [get_enviroment_var(pa) for pa in ['DB_STACK', 'DB_LAMBDA', 'LAMBDA_ENV']]
)

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

    invoke_response = boto3_client('lambda',
                                   aws_access_key_id=get_enviroment_var('USER_ACCESS'),
                                   aws_secret_access_key=get_enviroment_var('USER_SECRET')).invoke(
        FunctionName=DB_LAMBDA,
        InvocationType='RequestResponse',
        Payload=json.dumps(msg)
    )

    response = json.loads(invoke_response['Payload'].read())

    if response['status_code'] == 200:
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

    invoke_response = boto3_client('lambda',
                                   aws_access_key_id=get_enviroment_var('USER_ACCESS'),
                                   aws_secret_access_key=get_enviroment_var('USER_SECRET')).invoke(
        FunctionName=DB_LAMBDA,
        InvocationType='RequestResponse',
        Payload=json.dumps(msg)
    )

    response = json.loads(invoke_response['Payload'].read())

    if response['status_code'] == 200:
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

    invoke_response = boto3_client('lambda',
                                   aws_access_key_id=get_enviroment_var('USER_ACCESS'),
                                   aws_secret_access_key=get_enviroment_var('USER_SECRET')).invoke(
        FunctionName=ACL_MANAGEMENT_LAMBDA,
        InvocationType='RequestResponse',
        Payload=json.dumps(msg)
    )

    response = json.loads(invoke_response['Payload'].read())

    if response['status_code'] == 200:
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

            if not user_id:
                return internal_server_error()

            # get the permission of the user
            user_permission = json.loads(get_current_user_permission(user_id, query_string['permission']))

            if user_permission['authorized'] == 'True':
                # if yes, then get data
                return get_site_settings_values()
            else:
                # else, return bad request
                return forbidden()
        else:
            return bad_request(ADMIN_SETTINGS_URL_VALIDATOR.errors)
