#encoding:utf-8
import subprocess
import os,sys

def run(target, useCall=True, useShell=True, cwd=None):
    if useCall:
        target = "call " + target
    process = subprocess.Popen(target, shell=useShell, cwd=cwd)
    process.wait()
    return process.returncode

#ret = run(r'python db\drop_table.py')
#if ret != 0:
#    sys.exit(1)

ret = run(r'python manage.py syncdb')
if ret != 0:
    sys.exit(1)

#ret = run(r'python tools\sys_init.py')
#if ret != 0:
#    sys.exit(1)

#ret = run(r'')
#if ret != 0:
#    sys.exit(1)




#python tools\add_random_respondent.py
#python mc\update_report.py
