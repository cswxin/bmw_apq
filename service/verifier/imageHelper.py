#coding=utf-8

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import random
import verifySettings
import settings
import os

TrueTypeFontFile=verifySettings.TrueTypeFontFile
ParentDirectory=verifySettings.VERIFIERPATH
if not os.path.exists(TrueTypeFontFile):
    raise u"验证码字体文件不存在！"
font = ImageFont.truetype(TrueTypeFontFile,20,encoding='unic')

def generateCnChrImage(chineseCharacter,fileName):
    if type(chineseCharacter) != type(unicode()):
        raise 'need unicode string'
    elif len(chineseCharacter) > 4:
        raise 'unicode string must be only 4 characters'
    global TrueTypeFontFile, ParentDirectory, font
    image = Image.new('RGB',(65,26),0xFFFFFF)
    draw = ImageDraw.Draw(image)
    #~ draw.rectangle(((0,0),(85,26)),fill=0x7FFFD4)
    draw.rectangle(((0,0),(65,26)),fill=0xffffff)
    #~ for i in range(50):
        #~ draw.point((random.randint(0,100),random.randint(0,28)),fill=0x444444)
    draw.text((3,2), chineseCharacter, fill=0x444444, font=font)
    del draw
    
    if not os.path.exists(ParentDirectory):
        os.makedirs(ParentDirectory)
    
    saveTo = '%s/%s.jpg'%(ParentDirectory,fileName)
    image.save(saveTo)
    return fileName+'.jpg'
