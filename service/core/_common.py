#encoding:utf-8
import os, sys
from jinja2 import Template

def changeTupleValue(tupleData, value, replace):
    tmpList = list(tupleData)
    try:
        iIndex = tmpList.index(value)
        tmpList[iIndex] = replace
        return tuple(tmpList)
    except:
        raise ValueError, "Please check your value"

def jinja_render_to_string(tmpl_file, c={}):
    #返回的是Unicode字符串
    html = file(tmpl_file).read()
    html = html.decode('utf8')
    return Template(html).render(c)
