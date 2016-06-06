#encoding=utf8
'''
Created on 2012-9-20

@author: xingjun
'''
def index2colname(num):
    #int num = celNum + 1 #celNum是从0算起
    tem = ""
    ord_a = ord('A')
    while(num > 0):
        lo = (num - 1) % 26 #//取余，A到Z是26进制，
        tem = chr(lo + ord_a) + tem
        num = (num - 1) / 26 #//取模
    return tem

def colname2index(colname):
    reverse = colname[::-1]
    ord_a = ord('A')
    num = 0
    import math
    for index, ch in enumerate(reverse):
        ord_ch = ord(ch) 
        num += ((ord_ch - ord_a) % 26 + 1) * math.pow(26, index)
    return int(num)

if __name__ == '__main__':
    colname = index2colname(1029)
    print colname
    num = colname2index(colname)
    print num
