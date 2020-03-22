GET_ADMIN_SETTINGS_URL_SCHEMA = {
    'permission': {
        'type': 'string',
        'required': True,
        'allowed': ['admin.view']
    }
}

RUN_QUERY_SCHEMA = {
    'action': {
      'required': True,
        'type': 'string',
    },
    'queries': {
        'required': True,
        'type': 'list'
    }
}

ACL_MANAGEMENT_SCHEMA = {
    'action': {
        'required': True,
        'type': 'string'
    },
    'user_id': {
        'required': True,
        'type': 'string'
    },
    'permission': {
        'required': True,
        'type': 'string',
        'allowed': ['admin.view']
    }
}