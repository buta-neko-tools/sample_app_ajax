import os

BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES={
    'default':{
        'ENGINE':'django.db.backends.sqlite3',
        'NAME':os.path.join(BASE_DIR,'db.sqlite3'),
    }
}

DEBUG=True

SECRET_KEY='x%f7l8nabe@*%3_i^7q#xt25_2c^1t5w*jliq)-+fc$!#snq#d'