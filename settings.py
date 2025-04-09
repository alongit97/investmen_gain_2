from os import environ
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=0)
SESSION_CONFIGS = [
    {
        'name': 'investment_experiment_demo',
        'display_name': "Investment Experiment Demo",
        'num_demo_participants': 1,
        'app_sequence': ['investment_experiment_demo'],
        'debug_mode': True,
    },
]
LANGUAGE_CODE = 'en'
#REAL_WORLD_CURRENCY_CODE = 'ILS'
USE_POINTS = True
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = []
SESSION_FIELDS = []
ROOMS = []
#DEBUG = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']


