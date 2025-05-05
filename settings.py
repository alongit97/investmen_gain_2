from os import environ
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=0)
SESSION_CONFIGS = [
    {
        'name': 'Inv_Vee_3_1st_series_Inv_then_Out',
        'display_name': "IV, inv before out",
        'num_demo_participants': 1,
        'app_sequence': ['investment_experiment_demo'],
        'file_name': "Items_to_Present_Inv-Vee_3_1st-series_Inv-then-Out.xlsx",
        'investment_before_outcome': True,
    },

    {
        'name': 'Inv_Vee_3_1st_series_Out_then_Inv',
        'display_name': "IV, out before inv",
        'num_demo_participants': 1,
        'app_sequence': ['investment_experiment_demo'],
        'file_name': "Items_to_Present_Inv-Vee_3_1st-series_out-then-inv-new.xlsx",
        'investment_before_outcome': False,
    },

    {
        'name': 'Uni_3_1st_series_Inv_then_Out',
        'display_name': "U, inv before out",
        'num_demo_participants': 1,
        'app_sequence': ['investment_experiment_demo'],
        'file_name': "Items_to_Present_Uni_3_1st-series-Inv-then-Out.xlsx",
        'investment_before_outcome': True,
    },

    {
        'name': 'Uni_3_1st_series_Out_then_Inv',
        'display_name': "U, out before inv",
        'num_demo_participants': 1,
        'app_sequence': ['investment_experiment_demo'],
        'file_name': "Items_to_Present_Uni_3_1st-series-out-then-inv-new.xlsx",
        'investment_before_outcome': False,
    },

    {
        'name': 'Vee_3_1st_series_Inv_then_Out',
        'display_name': "V, inv before out",
        'num_demo_participants': 1,
        'app_sequence': ['investment_experiment_demo'],
        'file_name': "Items_to_Present_Vee_3_1st-series-Inv-then-Out.xlsx",
        'investment_before_outcome': True,
    },

    {
        'name': 'Vee_3_1st_series_Out_then_Inv',
        'display_name': "V, out before inv",
        'num_demo_participants': 1,
        'app_sequence': ['investment_experiment_demo'],
        'file_name': "Items_to_Present_Vee_3_1st-series-out-then-inv-new.xlsx",
        'investment_before_outcome': False,
    },
]
LANGUAGE_CODE = 'en'
#REAL_WORLD_CURRENCY_CODE = 'ILS'
USE_POINTS = True
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

EXTENSION_APPS = ['investment_experiment_demo.urls']
