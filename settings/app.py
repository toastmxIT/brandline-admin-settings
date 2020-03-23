from utils import bad_request, get_cognito_email, forbidden, get_user_id_by_email
from methods.get_settings import get_settings_from_event
from methods.patch_settings import patch_settings_from_event


def lambda_handler(event, context):
    if 'httpMethod' not in event:
        return bad_request('Not an HTTP invokation')

    # if it is an HTTP invokation, validate the token
    email = get_cognito_email(event)
    print(email)
    user_id = get_user_id_by_email(email)

    print(user_id)

    if not user_id:
        return forbidden()

    # for get or patch method, queryString should be sent with the permission type
    query_string = event['queryStringParameters'] if event['queryStringParameters'] else None

    if not query_string:
        return bad_request({'message': 'The event does not contain queryStringParameters'})

    if event['httpMethod'] == 'GET':
        return get_settings_from_event(query_string, user_id)
    elif event['httpMethod'] == 'PATCH':
        return patch_settings_from_event(event=event, query_string=query_string, user_id=user_id, email=email)

    return bad_request({'message': 'Bad request'})
