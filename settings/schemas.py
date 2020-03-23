GET_ADMIN_SETTINGS_URL_SCHEMA = {
    'permission': {
        'type': 'string',
        'required': True,
        'allowed': ['admin.view']
    }
}

PATCH_ADMIN_SETTINGS_SCHEMA = {
    'site_visibility': {
        'type': 'boolean',
        'required': False,
    },
    'title': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 150
    },
    'fontsize': {
        'type': 'integer',
        'required': False,
        'min': 1
    },
    'self_url': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 60
    },
    'coloraccent': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 6
    },
    'isdarkmode': {
        'type': 'integer',
        'required': False,
        'min': 1
    },
    'description': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 350
    },
    'copyright': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 150
    },
    'websiteurl': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 150
    },
    'brandmail': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 60
    },
    'brandlogourl': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 250
    },
    'faviconurl': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 250
    },
    'appiconurl': {
        'type': 'string',
        'required': False,
        'empty': False,
        'maxlength': 250
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