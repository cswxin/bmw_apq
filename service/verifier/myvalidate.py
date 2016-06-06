#coding=utf-8

import sys
import os
import datetime, time
import random
import threading
import traceback
from django.http import HttpResponse
import imageHelper
from imageHelper import generateCnChrImage
import verifySettings

from django.core.cache import cache

COUNT_KEY_ID = 'vad_count'

def _readcount():
    c = cache.get(COUNT_KEY_ID)
    if c is None:
        c = random.randint(1000,19999)
    return c
    
def _savecount(counter):
    cache.set(COUNT_KEY_ID,counter,30 * 60)
    
def generateVadImage():    
    cnCharacters = open(verifySettings.CharcterFile,'r').read().decode('utf-8')[1:]
    chrLength = len(cnCharacters) - 1
    
    uchr = ''
    for i in range(1,5):
        uchr = uchr + cnCharacters[random.randint(0,chrLength)]
    
    counter = _readcount()
    print counter
    
    try:
        generateCnChrImage(uchr,str(counter))
    except:
        return u'error:生成验证图片失败'
    
    cache.set('ver_%d' % counter,(uchr,datetime.datetime.now()),60)
    imgpath = '%s%s%s'%(verifySettings.VERIFIERURL,counter,'.jpg')
    
    counter += 1
    _savecount(counter)
    print counter
    
    return imgpath
    
def verify(numpath,uchr):
    try:
        num = int(os.path.split(numpath)[1].split('.')[0])
        if type(num) is int and type(uchr) is unicode:
            dataid = 'ver_%d' % num
            #print 'dataid',dataid
            ret = cache.get(dataid)
            if ret is None:
                return False
            
            usrcchar,dt = ret
            if not usrcchar.lower() == uchr.lower():
                return False
            
            return True
        else:
            return False
    except:
        return False

def refreshverifyimg(request):
    return HttpResponse(generateVadImage())
