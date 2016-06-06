#encoding:utf-8

import os
REL_SITE_ROOT = os.path.dirname(os.path.abspath(__file__))

REL_DEBUG = False
DATABASE_PATH = os.path.join(REL_SITE_ROOT, 'db')
if not os.path.exists(DATABASE_PATH):
    os.makedirs(DATABASE_PATH)
    
#DATABASE_ENGINE = 'sqlite3'
#DATABASE_NAME = os.path.join(DATABASE_PATH,'baoma.db3')
#DATABASE_USER = ''
#DATABASE_PASSWORD = ''
#DATABASE_HOST = '127.0.0.1'
#DATABASE_PORT = ''

DATABASE_ENGINE = 'django.db.backends.mysql'
DATABASE_NAME = 'a_bmw_apq'
DATABASE_USER = 'bmw'
DATABASE_PASSWORD = 'XRQUrKGg1QU'
DATABASE_HOST = '10.226.73.128'
DATABASE_PORT = ''

REL_MEDIA_URL = 'http://apq.surveylink.cn/file/'
#REL_MEDIA_URL = 'http://a.isurveylink.com:8888/file/'
#REL_MEDIA_URL = 'http://192.168.1.116:8000/file/'

REL_MEDIA_ROOT = os.path.join(REL_SITE_ROOT, 'file')

SCHEDULE_PATH = REL_MEDIA_ROOT

REL_ROOT_PATH = 'http://127.0.0.1:8000'

REL_CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
REL_CACHE_BACKEND = 'locmem:///?timeout=300&max_entries=30000'

if REL_DEBUG:
    REL_CACHE_TIME = 60
else:
    REL_CACHE_TIME = 600
