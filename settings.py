from os import environ
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
}
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=0)
SESSION_CONFIGS = [
    {
        'name': 'AC',
        'display_name': "p2-AC",
        'num_demo_participants': 1,
        'app_sequence': ['investment_gain_ratio'],
        'file_name': "p2-ac.docx",
    },

    {
        'name': 'AD',
        'display_name': "p2-AD",
        'num_demo_participants': 1,
        'app_sequence': ['investment_gain_ratio'],
        'file_name': "p2-ad.docx",
    },

    {
        'name': 'BC',
        'display_name': "p2-BC",
        'num_demo_participants': 1,
        'app_sequence': ['investment_gain_ratio'],
        'file_name': "p2-bc.docx",
    },

    {
        'name': 'BD',
        'display_name': "p2-BD",
        'num_demo_participants': 1,
        'app_sequence': ['investment_gain_ratio'],
        'file_name': "p2-bd.docx",
    },

    {
        'name': 'CA',
        'display_name': "p2-CA",
        'num_demo_participants': 1,
        'app_sequence': ['investment_gain_ratio'],
        'file_name': "p2-ca.docx",
    },

    {
        'name': 'CB',
        'display_name': "p2-CB",
        'num_demo_participants': 1,
        'app_sequence': ['investment_gain_ratio'],
        'file_name': "p2-cb.docx",
    },

    {
        'name': 'DA',
        'display_name': "p2-DA",
        'num_demo_participants': 1,
        'app_sequence': ['investment_gain_ratio'],
        'file_name': "p2-da.docx",
    },

    {
        'name': 'DB',
        'display_name': "p2-DB",
        'num_demo_participants': 1,
        'app_sequence': ['investment_gain_ratio'],
        'file_name': "p2-db.docx",
    }
]
LANGUAGE_CODE = 'en'
#REAL_WORLD_CURRENCY_CODE = 'ILS'
USE_POINTS = False
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = []
SESSION_FIELDS = []
ROOMS = []
DEBUG = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

EXTENSION_APPS = ['investment_gain_ratio.urls']
