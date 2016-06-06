#encoding:utf-8

import os,sys
sys.path.insert(0,os.path.abspath(os.curdir))

#from django.core.mail import send_mail
import os
from django.core.mail import EmailMultiAlternatives
from djangodblog.models import *


subject = 'Error traceback in gfk mcreport system!'
sender = 'isurveylink@sohu.com'
recver = ['harry.liang@idiaoyan.com','roboter.song@idiaoyan.com','forrest.liu@idiaoyan.com']

last_id_file = 'last_id_of_djangodblog.txt'

def main():
    if not os.path.exists(last_id_file):
        err_list = Error.objects.all().order_by('-id')[:1]
        if err_list:
            last_id = err_list[0].id
        else:
            last_id = 0
    else:
        last_id = file(last_id_file).read().strip()

    error_list = []

    for error in Error.objects.filter(id__gt=int(last_id))[:10]:
        #print error.traceback
        last_id = error.id
        if error.traceback.find('IOError: Client read error (Timeout?)') >= 0:
            continue
        error_list.append(error)
    msg_list = []

    f = open(last_id_file,'wb')
    f.write(str(last_id))
    f.close()

    msg_list.append("""
    <html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    </head>
    <body>
        <style type="text/css">
        body,td {font-size:12px;}
        table {border:solid 1px gray;}
        td {border-right:solid 1px gray;border-bottom:solid 1px gray;height:20px;text-align:center;}
        </style>
        <table>
    """)

    for error in error_list:
        msg_list.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (error.url,error.traceback,error.datetime,error.server_name,error.id))

    msg_list.append('</table></body></html>')

    message = '\n'.join(msg_list)
    if error_list:
        #send_mail(subject,message,sender,recver,fail_silently=False)
        text_content = 'Please view in HTML format'
        msg = EmailMultiAlternatives(subject, text_content, sender, recver)
        msg.attach_alternative(message, "text/html")
        msg.send()
    
if __name__ == '__main__':
    main()

