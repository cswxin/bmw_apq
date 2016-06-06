#encoding:utf-8
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.curdir))
from mc.models import ReportImage, Dealer, Paper
from django.contrib.auth.models import User 
from django.conf import settings
from datetime import datetime


IMAGE_RES_PATH = os.path.join(settings.RESOURCES_ROOT, u'first/images/')
replaceuploadchar = ['%20', ' ', '(', ')', '!']

def upload_image_path(filename):
    for c in replaceuploadchar:
        filename = filename.replace(c, '_')
    nowday = datetime.today()
    import random
    ranid = random.randint(1, 9999)
    nowday = datetime.today()
    return u'image/%d/%d/%d/%d_%s' % (nowday.year, nowday.month, nowday.day, ranid, filename)


def upload_images():
    images = os.listdir(IMAGE_RES_PATH)
    user = User.objects.get(pk=1)
    for dn in images:
        dealer_code = dn.split('-')[1]
        print  dn, dealer_code
        try:
            dealer = Dealer.objects.get(name=dealer_code)
            fwpaper = Paper.objects.get(paper_type='GFK', dealer=dealer, term__id=5)
            fullpath = os.path.join(IMAGE_RES_PATH, dn)
            imgstrs = ','.join([ rimg.image for rimg in ReportImage.objects.filter(paper=fwpaper)])
            if os.path.isdir(fullpath):
                pics = os.listdir(fullpath)
                for pic in pics:
                    picpath = os.path.join(fullpath, pic)
                    if imgstrs.find(pic) == -1:
                        filename = upload_image_path(pic)
                        destpath = os.path.join(settings.MEDIA_ROOT, filename)
                        shutil.copy(picpath, destpath)
                        print  fwpaper.id, filename
                        ReportImage.objects.get_or_create(user=user, image=filename, paper=fwpaper)
                    else:
                        print u'%s %s existed' % (dealer_code, pic)
                    os.remove (picpath)
        except Exception, ex:
            print ex
            continue
         
        
if __name__ == '__main__':
    upload_images()
