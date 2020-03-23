import json
import sys

import psycopg2
from cerberus import Validator
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor

from schemas import RUN_QUERY_SCHEMA

rds_host = 'brandline.con1rcg8el6v.us-west-2.rds.amazonaws.com'
name = 'masterDB'
password = 'sm12345678'
db_name = 'brandline'
port = '5432'

RUN_QUERY_VALIDATOR = Validator(RUN_QUERY_SCHEMA)

ALLOWED_ACTIONS = ['run']


def lambda_handler(event):
    body = event["body"] if event["body"] else None

    if not body:
        return 'bad_request', {'message': 'Event request does not contain body object'}

    if 'action' not in body:
        return 'bad_request', {'message': 'Body does not contain \'action\' key'}

    if body["action"] not in ALLOWED_ACTIONS:
        return 'bad_request', {
            'message': 'Body does not contain a valid action. Valid actions are: ' + ','.join(ALLOWED_ACTIONS)}

    if body["action"] == 'run':
        if RUN_QUERY_VALIDATOR.validate(body):
            queries = body['queries']
            response = execute_queries(queries)
            return 'ok', response
        else:
            return 'bad_request', RUN_QUERY_VALIDATOR.errors


def execute_queries(queries):
    """
    This function fetches content from MySQL RDS instance
    """
    conn = dbconnect()

    result = []

    for query in queries:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                cur.execute(query)
                rows = cur.fetchall()
                result.append(json.dumps(rows, indent=2))
            except Exception as e:
                print(e)
    conn.commit()
    conn.close()
    return result


def dbconnect():
    try:
        return psycopg2.connect(host=rds_host, user=name, password=password, dbname=db_name, port=port)
    except OperationalError as e:
        err_type, err_obj, traceback = sys.exc_info()
        print(err_type)
        print(err_obj)
        print(traceback)
        sys.exit()