#encoding:utf-8

def to_unicode(text):
    if isinstance(text,unicode):
        return text
    text = str(text)
    try:
        return text.decode('utf-8')
    except UnicodeError:
        try:
            return text.decode('gb18030')
        except UnicodeError:
            return u'UnicodeError'

def to_gbk(text):
    if text is None:
        return None
    elif isinstance(text,unicode):
        return text.encode('gb18030')
    else:
        try:
            return text.decode('utf-8').encode('gb18030')
        except UnicodeError:
            return text

def to_utf8(text):
    if isinstance(text,unicode):
        return text.encode('utf-8')
    else:
        try:
            text.decode('utf-8') #这里是通过解码来检查是否是utf-8编码，不能直接返回解码后的内容，只能返回解码前的内容！
            return text            
        except UnicodeError:
            pass
        
        try:
            return text.decode('gb18030').encode('utf-8')
        except UnicodeError:
            return 'UnicodeError'

