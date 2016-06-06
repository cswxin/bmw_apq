#coding=utf-8

import settings
import os

VERIFIERPATH= os.path.join(settings.MEDIA_ROOT,'verimages','myverifier')
VERIFIERURL= '%s%s' %(settings.MEDIA_URL,'verimages/myverifier/')
LOGDIR=os.path.join(settings.MEDIA_ROOT,'website_log')
CharcterFile=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cncharacter.txt')
TrueTypeFontFile=os.path.join(os.environ["SYSTEMROOT"],'Fonts','TAHOMA.TTF')