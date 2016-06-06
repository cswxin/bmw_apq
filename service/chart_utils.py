#encoding:utf-8
import os,sys
if __name__ == '__main__':
    sys.path.insert(0,os.path.abspath(os.curdir))
import mc
from mc.models import Term,Dealer,Report
from django.db import connection


from pychartdir import *
import utils
import settings

BASE_COLOR = [0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,
              0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5,0x4180C5]


def create_simple_xychart(title,labels,data,mark_value=None,format='{value|1}',fontAngle=0,x=560,y=220,swapxy=False,Scale=100):
    colors = BASE_COLOR
    c = XYChart(x, y)
    c.setBackground(c.linearGradientColor(0, 0, 0, c.getHeight(), '0xFEFEFE', '0xFFFFFF'),'0X666666')

    title_height = 0

    c.addLine(20, title_height, c.getWidth() - 21, title_height, '0xffffff')

    plot_width = 30+50*len(labels)
    c.setPlotArea(70, 50, plot_width, 170, -1, -1, Transparent, '0xffffff')
    if swapxy:
        c.swapXY()
    title = c.addTitle(utils.to_utf8(title), "simsun.ttc", 12)
    title.setMargin2(20, 0, 10, 30)
    
    layer = c.addBarLayer3(data, colors)
    layer.setBorderColor(Transparent, softLighting(Right))
    layer.setAggregateLabelFormat(format)
    font_size = 8 if fontAngle == 0 else 7
    layer.setAggregateLabelStyle("simsun.ttc", font_size)
    layer.setBarWidth(x,15)
    
    xAxis = c.xAxis()
    xAxis.setLabels(labels)
    
    c.yAxis().setLinearScale(0,Scale)
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)
    c.xAxis().setTickColor(Transparent)
    c.xAxis().setLabelStyle("simsun.ttc", 9, 0x0, fontAngle)
    c.yAxis().setLabelStyle("simsun.ttc", 9)
    c.yAxis2().setLabelStyle("simsun.ttc", 9)
    
#    if mark_value:
#        markData = [mark_value for i in range(len(data))]
#        markLayer = c.addBoxWhiskerLayer(None, None, None, None, markData, -1, '0xff0000')

    c.packPlotArea(20, title_height + 40, c.getWidth() - 30, c.getHeight() - 15)

    return c.makeChart2(PNG)

def create_multi_xychart(title, labels, series_list,series_top,Scale=100):
    # Create a XYChart object of size 540 x 375 pixels
    c = XYChart(900, 320)
    # Add a title to the chart using 18 pts Times Bold Italic font
    #c.addTitle("Average Weekly Network Load", "timesbi.ttf", 18)
    title = c.addTitle(utils.to_utf8(title), "simsun.ttc", 12)
    title.setMargin2(20, 0, 10, 30)
    
    color_list = BASE_COLOR
    
    # Set the plotarea at (50, 55) and of 440 x 280 pixels in size. Use a vertical
    # gradient color from light red (ffdddd) to dark red (880000) as background. Set
    # border and grid lines to white (ffffff).
    plot_width = 30+140*len(labels)
    c.setPlotArea(50, 90, plot_width, 200, c.linearGradientColor(60, 40, 60, 280, 0xffffff,
    0xd8e2ec), -1, 0xffffff, 0xffffff)
    
    legendBox = c.addLegend(50, 30, 0, "simsun.ttc", 10)
    legendBox.setBackground(Transparent)
    #legendBox.setAlignment(TopCenter)
    legendBox.setHeight(30)
    
    # Set the x axis labels
    c.xAxis().setLabels([utils.to_utf8(label) for label in labels])
    
    # Draw the ticks between label positions (instead of at label positions)
    c.xAxis().setTickOffset(0.5)
    
    # Set axis label style to 8pts Arial Bold
    c.xAxis().setLabelStyle("simsun.ttc", 9)
    c.yAxis().setLabelStyle("simsun.ttc", 9)
    
    # Set axis line width to 2 pixels
    c.xAxis().setWidth(2)
    c.yAxis().setWidth(2)
    c.yAxis2().setWidth(1)
    
    # Add axis title
    c.yAxis().setTitle("得分/Score", "simsun.ttc", 9)
    c.yAxis().setLinearScale(0,Scale)
    # Add a multi-bar layer with 3 data sets and 4 pixels 3D depth
    #~ layer = c.addBarLayer2(Side, 1)
    layer = c.addBarLayer()
    layer.setBarGap(0.2)

    for index,series in enumerate(series_list):
        layer.addDataSet(series['value'], color_list[index%len(color_list)], utils.to_utf8(series['name']))
    
    #~ legendBox.addKey2(2,utils.to_utf8(series_top['name']), 0xFF6900, 2)
    #~ markLayer = c.addBoxWhiskerLayer(None, None, None, None, series_top['value'], -1, 0xFF6900)
    #~ markLayer.setLineWidth(2)
    #~ markLayer.setDataGap(0.1)
    #~ markLayer.setDataLabelStyle("simsun.ttc", 9)
    #~ markLayer.setDataLabelFormat("{value|1}")
    
    # Set bar border to transparent. Use soft lighting effect with light direction from
    # top.
    layer.setBorderColor(Transparent, softLighting(Top))
    #layer.setBorderColor(Transparent, barLighting(0.75, 2.0))
    
    layer.setAggregateLabelFormat("{value|1}")
    
    # output the chart
    return c.makeChart2(PNG)
    
#制作柱线对比图
def create_bar_line_xychart(title,labels,barData,lineData=None,lineData2=None,mark_value=None,format='{value|1}',fontAngle=0,x=560,y=220,swapxy=False,Scale=100,legendVertical=False):
    
    # 创建XYChart对象，大小x*y
    c = XYChart(x, y)
    
    #为输出图片创建边框
    c.setBackground(c.linearGradientColor(0, 0, 0, c.getHeight(), '0xFEFEFE', '0xFFFFFF'),'0X666666')
    c.addLine(20, 0, c.getWidth() - 21, 0, '0xffffff')
    
    # 图表增加标题，大小12px
    # 标题设置对齐，左右上下
    title = c.addTitle(title, 'simsun.ttc', 12)
    title.setMargin2(0, 0, 10, 30)
    
    plot_width = 30+50*len(labels)
    
    plotArea = c.setPlotArea(70, 50, plot_width, 170, -1, -1, Transparent, c.dashLineColor('0x444444', DotLine))
    
    if swapxy:
        labels.reverse()
        barData.reverse()
        c.swapXY()
        
    #如果存在线数据，绘制线性层
    if lineData:
        lineLayer = c.addLineLayer2()
        if swapxy:
            lineData.reverse()
        lineLayer.addDataSet(lineData, '0x00FF00', u"区域").setDataSymbol(GlassSphere2Shape, 7)
        lineLayer.setLineWidth(2)
        if legendVertical:
            legendBox = c.addLegend(x - 70, 0, 1, "simsun.ttc", 9)
        else:
            legendBox = c.addLegend(x/2 + 100 , 10, 0, "simsun.ttc", 9)
        legendBox.setAlignment(TopRight2)
        legendBox.setBackground(Transparent, Transparent)
        legendBox.setLineStyleKey()
    if lineData2:
        lineLayer = c.addLineLayer2()
        if swapxy:
            lineData2.reverse()
        lineLayer.addDataSet(lineData2, '0xFF0000', u"全国").setDataSymbol(GlassSphere2Shape, 7)
        lineLayer.setLineWidth(2)
        if legendVertical:
            legendBox = c.addLegend(x - 70, 0, 1, "simsun.ttc", 9)
        else:
            legendBox = c.addLegend(x/2 + 100 , 10, 0, "simsun.ttc", 9)
        legendBox.setAlignment(TopRight2)
        legendBox.setBackground(Transparent, Transparent)
        legendBox.setLineStyleKey()
    #创建柱状层
    barLayer = c.addBarLayer(barData, '0x0070C0', "经销商")
    barLayer.setBorderColor(Transparent, softLighting(Left))
    barLayer.setBarWidth(560,50)
    barLayer.setAggregateLabelFormat(format)
    font_size = 9 if fontAngle == 0 else 7
    barLayer.setAggregateLabelStyle("simsun.ttc", font_size)
    
    c.xAxis().setLabels(labels)
    c.yAxis().setLinearScale(0, Scale)

    c.yAxis().setLabelStyle("simsun.ttc", 9)
    c.xAxis().setLabelStyle("simsun.ttc", 9, 0x0, fontAngle)
    
    c.packPlotArea(20, 60, c.getWidth() - 30, c.getHeight() - 15)
    return c.makeChart2(PNG)

def test():
    from random import randint
    title = '经销商总得分 Total Score'
    labels = ['第一期/W1','第二期/W2','第三期/W3','第四期/W4']
    data_list = []
    series_name_list = [
        u'当前经销商得分',
        u'所在城市平均得分',
        u'所属区域平均得分',
        u'全国平均得分',
    ]
    series_top = dict(name=u'全国最佳经销商得分',value=[randint(1,10) for i in labels])
    
    series_list = []
    for i,series_name in enumerate(series_name_list):
        value = []
        for label in labels:
            value.append(randint(1,10))
        series_list.append(dict(name=series_name,value=value))
    
    save_as = 'r:/test.png'
    data = create_multi_xychart(title,labels,series_list,series_top)
    file(save_as,'wb').write(data)
    return data

def test1():
    title = '各期次得分对比'
    # The data for the bar chart
    data = [80, 90, 57, 86, 95]

    # The labels for the bar chart
    labels = ["第一期/W1", "第二期/W2", "2003", "2004", "2005"]
    
    save_as = 'r:/test1.png'
    data = create_simple_xychart(title,labels,data)
    file(save_as,'wb').write(data)
    return data

#总得分与环节得分
def create_dealer_score_chart(dealer,term):
    cp_list = mc.get_checkpoint_group_list_with_total()
    data = mc.get_dealer_score(term,dealer)
    
    #labels = [cp.name_abbr for cp in cp_list]
    labels = [add_line_break(cp.name_abbr,4) for cp in cp_list]
    labels = [add_line_break(label,9) for label in labels]
    
    file_name = 'dealer_score_%s_%s_%s.png' % (dealer.id,term.id,utils.get_verify_code2(dealer.id,term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    
    title = u'总得分与环节得分'
    if term.id > 1:
        term_last = mc.get_term(term.id-1)
        dataLine = mc.get_dealer_score(term_last,dealer)
        data = create_bar_line_xychart(title,labels,data,dataLine,mark_value=data[0])
    else:
        data = create_bar_line_xychart(title,labels,data,mark_value=data[0])
    file(save_as,'wb').write(data)
    return file_name

#总得分分布情况
def create_dealer_score_group_by_chart(term,labels,parent_name,data):

    title = u'经销商得分分布情况'
    
    file_name = 'dealer_score_group_by_%s_%s_%s.png' % (term.id,parent_name,utils.get_verify_code2(term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    #data = create_simple_xychart(title,labels,data,mark_value=None,format='{value|1}%')
    if  term.id > 1:
        term_last = mc.get_term(term.id-1)
        dataLine,labels_last = mc.get_dealer_score_group_by(term_last)
        data = create_bar_line_xychart(title,labels,data,dataLine,mark_value=None,format='{value|1}%')
    else:
        data = create_bar_line_xychart(title,labels,data,mark_value=None,format='{value|1}%')
    file(save_as,'wb').write(data)
    return file_name

#大区得分与全国对比
def create_region1_score_chart(term,selected_dealer,report_nation,labels,data):
    title = u'大区总得分'
    
    file_name = 'region1_score_%s_%s_%s.png' % (term.id,selected_dealer.id,utils.get_verify_code2(term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    #data = create_simple_xychart(title,labels,data,mark_value=report_nation.score,format='{value|1}')
    if  term.id > 1:
        term_last = mc.get_term(term.id-1)
        report_nationLine,labelsLine,dataLine = mc.get_region1_score_chart_data(term_last)
        data = create_bar_line_xychart(title,labels,data,dataLine,mark_value=report_nation.score)
    else:
        data = create_bar_line_xychart(title,labels,data,mark_value=report_nation.score)
    file(save_as,'wb').write(data)
    return file_name

#小区得分与全国对比
def create_region2_score_chart(term,selected_dealer,report_nation,labels,data):
    title = u'小区总得分'
    file_name = 'region2_score_%s_%s_%s.png' % (term.id,selected_dealer.id,utils.get_verify_code2(term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    #data = create_simple_xychart(title,labels,data,mark_value=report_nation.score,format='{value|1}',fontAngle=90)
    if  term.id > 1:
        term_last = mc.get_term(term.id-1)
        report_nationLine,labelsLine,other_labelLine,dataLine = mc.get_region2_score_chart_data(term_last)
        data = create_bar_line_xychart(title,labels,data,dataLine,mark_value=report_nation.score,format='{value|1}',swapxy=True,y=600)
    else:
        data = create_bar_line_xychart(title,labels,data,mark_value=report_nation.score,format='{value|1}',swapxy=True,y=600)
    file(save_as,'wb').write(data)
    return file_name
    
#特约商评估结果对比图
def create_region3_score_chart(term,selected_dealer,labels,data,data_last=None):
    title = u'环节得分'
    
    labels = [add_line_break(label,8) for label in labels]
    
    file_name = 'region3_score_%s_%s_%s.png' % (term.id,selected_dealer.id,utils.get_verify_code2(term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    if data_last:
        data = create_bar_line_xychart(title,labels,data,data_last,swapxy=True,x=400,y=330,format='{value|1}',legendVertical=True)
    else:
        data = create_bar_line_xychart(title,labels,data,swapxy=True,x=400,y=330,format='{value|1}',legendVertical=True)
    file(save_as,'wb').write(data)
    return file_name

def truncate_hanzi (s, num):
    from django.utils.encoding import force_unicode
    import re
    s = force_unicode(s)
    length = int(num)
    if length <= 0 :
        return u'...'
    re_alnum = re . compile( ur'[a-zA-Z0-9_\-\u00c0-\u02af\u0370-\u1fff]' , re . U)
    re_hanzi = re . compile( ur'[\u3040-\ufaff]' , re . U)
    hanzi = u''
    hanzi_len = 0
    word_temp = u''
    for char in s:
        if re_alnum.match(char):
            hanzi += char
            hanzi_len += 0.5
            if hanzi_len >= length:
                if not hanzi.endswith( '...' ):
                    hanzi += '...'
                break
            else:
                continue
        if hanzi_len >= length:
            if not hanzi.endswith( '...' ):
                hanzi += '...'
            break
        hanzi_len += 1
        hanzi += char

    return hanzi

    
#如果单行汉字s显示过长，在num位置增加换行符
def add_line_break(s, num):
    from django.utils.encoding import force_unicode
    import re
    s = force_unicode(s)
    length = int(num)
    if length <= 0 :
        return u'\n'
    hanzi = u''
    hanzi_len = 0
    
    for char in s:
            
        if hanzi_len == length and not hanzi.endswith( '\n' ):
            hanzi += '\n'
            
        hanzi_len += 1
        hanzi += char

    return hanzi
    

def create_simple_row_xychart(title,labels,data,mark_value=None,format='{value|1}',fontAngle=0,Scale=100,width=800):
    new_labels = [truncate_hanzi(label,25) for label in labels]
    colors = BASE_COLOR
    chart_height = 60+20*len(new_labels)
    c = XYChart(width, chart_height)

    c.setBackground(c.linearGradientColor(0, 0, 0, c.getHeight(), '0xFEFEFE', '0xFFFFFF'),'0X666666')
    #~ c.setRoundedFrame('0xffffff', 30, 0, 30, 0)

    title_height = 0

    c.addLine(20, title_height, c.getWidth() - 21, title_height, '0xffffff')

    plot_height = chart_height-30
    c.setPlotArea(70, 50, 270, plot_height,  -1, -1, Transparent, '0xffffff')

    c.swapXY()

    layer = c.addBarLayer3(data, colors)
#    layer.setBorderColor(Transparent, softLighting(Right))
    layer.setAggregateLabelFormat(format)
    layer.setAggregateLabelStyle("simsun.ttc", 8)
    
    xAxis = c.xAxis()
    xAxis.setLabels(new_labels)
    xAxis.setReverse()
    c.yAxis().setLinearScale(0,Scale)
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)
    c.xAxis().setTickColor(Transparent)
    c.xAxis().setLabelStyle("simsun.ttc", 9, 0x0, fontAngle)
    c.yAxis().setLabelStyle("simsun.ttc", 9)
    c.yAxis2().setLabelStyle("simsun.ttc", 9)
    
    if mark_value:
        markData = [mark_value for i in range(len(data))]
        markLayer = c.addBoxWhiskerLayer(None, None, None, None, markData, -1, '0xff0000')
        markLayer.setLineWidth(2)
        markLayer.setDataGap(0.1)

    c.packPlotArea(20, title_height + 15, c.getWidth() - 40, c.getHeight() - 15)

    return c.makeChart2(PNG)

def create_dealer_index_xychart(title,labels,score,mark_value=None,format='{value|1}',fontAngle=0,Scale=100):
    new_labels = [truncate_hanzi(label,25) for label in labels]
    colors = BASE_COLOR
    chart_height = 60+20*len(new_labels)
    c = XYChart(400, chart_height)
    title = c.addTitle(utils.to_utf8(title), "simsun.ttc", 12)
    title.setMargin2(20, 0, 10, 30)
    c.setBackground(c.linearGradientColor(0, 0, 0, c.getHeight(), '0xFEFEFE', '0xFFFFFF'),'0X666666')
    title_height = 0
    c.addLine(20, title_height, c.getWidth() - 21, title_height, '0xffffff')
    plot_height = chart_height-30
    c.setPlotArea(70, 50, 270, plot_height,  -1, -1, Transparent, '0xffffff')
    layer = c.addBarLayer3(score, colors)
#    layer.setBorderColor(Transparent, softLighting(Right))
    layer.setAggregateLabelFormat(format)
    layer.setAggregateLabelStyle("simsun.ttc", 8)
    
    xAxis = c.xAxis()
    xAxis.setLabels(new_labels)
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)
    c.xAxis().setTickColor(Transparent)
    c.xAxis().setLabelStyle("simsun.ttc", 9, 0x0, fontAngle)
    c.yAxis().setLabelStyle("simsun.ttc", 9)
    c.yAxis2().setLabelStyle("simsun.ttc", 9)
    c.yAxis().setLinearScale(0,Scale)

    c.packPlotArea(20, title_height + 15, c.getWidth() - 30, c.getHeight() - 15)

    return c.makeChart2(PNG)

def create_sub_checkpoint_chart(checkpoint_group,dealer,term,score,data,data_last=None):
    labels = [cp.name+'. '+cp.desc for cp in checkpoint_group.child_list]
    title = checkpoint_group.desc
    file_name = "sub_checkpoint_%s_%s_%s_%s.png" %(checkpoint_group.id,dealer.id,term.id,utils.get_verify_code2(term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    #data = create_simple_row_xychart(title,labels,data,mark_value=score,format='{value|1}')
    
    new_labels = [truncate_hanzi(label,25) for label in labels]
    chart_height = 60+20*len(new_labels)
    data = create_bar_line_xychart(title,new_labels,data,data_last,mark_value=score,swapxy=True,x=860,y=chart_height)
    
    file(save_as,'wb').write(data)
    return file_name

def create_cp_chart(dealer,term,cp,labels,data,data_last=None):
    if cp:
        title = cp.desc+u"得分对比"
    else:
        title = "总得分对比"
    file_name = "cp_chart_%s_%s_%s_%s.png" %(cp.id,term.id,dealer.id,utils.get_verify_code2(term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    #data = create_simple_row_xychart(title,labels,data,format='{value|1}',width=420)
    
    data = create_bar_line_xychart(title,labels,data,data_last,x=420,swapxy=True,legendVertical=True)
    
    file(save_as,'wb').write(data)
    return file_name

def create_dealer_index_chart(labels,checkpoint_group,selected_dealer,term,score):
    file_name = "dealer_index_%s_%s_%s_%s.png" %(checkpoint_group.id,selected_dealer.id,term.id,utils.get_verify_code2(term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    title = u'环节得分比较'
    data = create_dealer_index_xychart(title,labels,score,mark_value=score,format='{value|1}')
    file(save_as,'wb').write(data)
    return file_name

def create_round_meter_chart(selected_dealer,term,checkpoint,value):
    angular_meter = AngularMeter(100,100,silverColor(),'0x000000', -2)
    angular_meter.setRoundedFrame()
    angular_meter.setMeter(50,50,45,-135,135)
    angular_meter.setScale(0,100,10,5,1)
    angular_meter.setLabelStyle("normal",7)
    angular_meter.setLineWidth(0, 2, 1)
    angular_meter.addRing(0, 90, metalColor('0x9999dd'))
    angular_meter.addRing(88, 90, '0x6666ff')
    angular_meter.addZone(0, 60, '0x99ff99')
    angular_meter.addZone(60, 80, '0xffff00')
    angular_meter.addZone(80, 100, '0xff3333')
    angular_meter.addText(50, 70, u"总分", "simsun.ttc", 8,TextColor, Center)
    angular_meter.addText(50, 85, angular_meter.formatValue(value, "1"),"Arial", 8, '0xffffff', Center
    ).setBackground('0x000000', '0x000000', -1)
    
    angular_meter.addPointer(value, '0x40333399')
    file_name = "round_meter_%s_%s_%s_%s.png" %(selected_dealer.id,term.id,checkpoint.id,utils.get_verify_code2(term.id))
    save_as = '%s/shouhou/static/mcview/chart/%s' % (settings.SITE_ROOT,file_name)
    if not os.path.exists(os.path.dirname(save_as)):
        os.makedirs(os.path.dirname(save_as))
    data = angular_meter.makeChart2(PNG)
    file(save_as,'wb').write(data)
    return file_name
    

if __name__ == '__main__':
    pass
