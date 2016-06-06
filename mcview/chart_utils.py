#encoding:utf-8
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from pychartdir import Bottom, XYChart, PNG, Transparent, Side, softLighting, Top, Right, TouchBar, TopCenter, PolarChart, goldColor, metalColor, whiteOnBlackPalette, barLighting
import utils

BASE_COLOR = [0x2F8AE2, 0x959896, 0xB3C9F3, 0xA2E5E5, 0xFF6900, ]
BASE_COLOR = [0x7393CC, 0xE1974C, 0x84BA5C, 0xD35D5F, 0x969799, 0xCBC273, 0x8C63A7, ]

def create_simple_xychart(title, labels, data):
    # The colors for the bars
    colors = BASE_COLOR

    # Create a PieChart object of size 600 x 380 pixels.
    c = XYChart(380, 50 + 30 * len(labels))

    # Use the white on black palette, which means the default text and line colors are
    # white
    #~ c.setColors(whiteOnBlackPalette)

    # Use a vertical gradient color from blue (0000cc) to deep blue (000044) as
    # background. Use rounded corners of 30 pixels radius for the top-left and
    # bottom-right corners.
    c.setBackground(c.linearGradientColor(0, 0, 0, c.getHeight(), '0xEFF1F1', '0xDEE3E4')
        )
    #~ c.setRoundedFrame('0xffffff', 30, 0, 30, 0)

    # Add a title using 18 pts Times New Roman Bold Italic font. Add 6 pixels top and
    # bottom margins to the title.
    #title = c.addTitle(title, "simsun.ttc", 12)
    #title.setMargin2(0, 0, 6, 0)
    #title_height = 25
    title_height = 0

    # Add a separator line in white color just under the title
    #~ c.addLine(20, title.getHeight(), c.getWidth() - 21, title.getHeight(), '0xffffff')
    c.addLine(20, title_height, c.getWidth() - 21, title_height, '0xffffff')

    # Tentatively set the plotarea at (70, 80) and of 480 x 240 pixels in size. Use
    # transparent border and white grid lines
    c.setPlotArea(70, 70, 360, 30 + 30 * len(labels), -1, -1, Transparent, '0xffffff')

    # Swap the axis so that the bars are drawn horizontally
    c.swapXY()

    # Add a multi-color bar chart layer using the supplied data. Use bar gradient
    # lighting with the light intensity from 0.75 to 2.0
    layer = c.addBarLayer3(data, colors)
    #layer.setBorderColor(Transparent, barLighting(0.75, 2.0))
    layer.setBorderColor(Transparent, softLighting(Right))
    # Set the aggregate label format
    layer.setAggregateLabelFormat("{value|1}")

    # Set the aggregate label font to 8 point Arial Bold Italic
    layer.setAggregateLabelStyle("simsun.ttc", 8)



    # Set the labels on the x axis.
    c.xAxis().setLabels(labels)

    # Show the same scale on the left and right y-axes
    #c.syncYAxis()

    # Set the bottom y-axis title using 10pt Arial Bold font
    c.yAxis().setTitle("总得分 Total Score", "simsun.ttc", 9)

    # Set y-axes to transparent
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)

    # Disable ticks on the x-axis by setting the tick color to transparent
    c.xAxis().setTickColor(Transparent)

    # Set the label styles of all axes to 8pt Arial Bold font
    c.xAxis().setLabelStyle("simsun.ttc", 9)
    c.yAxis().setLabelStyle("simsun.ttc", 9)
    c.yAxis2().setLabelStyle("simsun.ttc", 9)
    
    c.yAxis().setLinearScale(0, 100)
    # Adjust the plot area size, such that the bounding box (inclusive of axes) is 30
    # pixels from the left edge, 25 pixels below the title, 50 pixels from the right
    # edge, and 25 pixels from the bottom edge.
    c.packPlotArea(20, title_height + 15, c.getWidth() - 30, c.getHeight() - 15)

    # Output the chart
    return c.makeChart2(PNG)

def create_multi_xychart(title, labels, series_list, series_top, maxv=100):
    
#    labels = [labels[0]]
    series_list = [series_list[0]]
    
    # Create a XYChart object of size 540 x 375 pixels
    c = XYChart(900, 320)
    # Add a title to the chart using 18 pts Times Bold Italic font
    #c.addTitle("Average Weekly Network Load", "timesbi.ttf", 18)
    title = c.addTitle(utils.to_utf8(title), "simsun.ttc", 12)
    title.setMargin2(20, 0, 5, 30)
    
    color_list = BASE_COLOR
    
    # Set the plotarea at (50, 55) and of 440 x 280 pixels in size. Use a vertical
    # gradient color from light red (ffdddd) to dark red (880000) as background. Set
    # border and grid lines to white (ffffff).
    chart_width = 30 + 190 * len(labels)
    c.setPlotArea(50, 90, chart_width, 200, c.linearGradientColor(60, 40, 60, 280, 0xffffff,
    0xd8e2ec), -1, 0xffffff, 0xffffff)
    
    legendBox = c.addLegend(50, 16, 0, "simsun.ttc", 10)
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
    
    c.yAxis().setLinearScale(0, maxv)
    
    # Add a multi-bar layer with 3 data sets and 4 pixels 3D depth
    #~ layer = c.addBarLayer2(Side, 1)
    layer = c.addBarLayer()
    layer.setBarGap(0.2)
    layer.setBarWidth(150, 48)

    for index, series in enumerate(series_list):
        layer.addDataSet(series['value'], color_list[index % len(color_list)], utils.to_utf8(series['name']))
    
    if series_top:
        legendBox.addKey2(2, utils.to_utf8(series_top['name']), 0xFF6900, 2)
        markLayer = c.addBoxWhiskerLayer(None, None, None, None, series_top['value'], -1, 0xFF6900)
        markLayer.setLineWidth(2)
        markLayer.setDataGap(0.1)
        markLayer.setDataLabelStyle("simsun.ttc", 9)
        markLayer.setDataLabelFormat("{value|1}")
    
    # Set bar border to transparent. Use soft lighting effect with light direction from
    # top.
    layer.setBorderColor(Transparent, softLighting(Top))
    #layer.setBorderColor(Transparent, barLighting(0.75, 2.0))
    
    layer.setAggregateLabelFormat("{value|1}")
    
    # output the chart
    return c.makeChart2(PNG)

def create_history_now_future_xychart(title, labels, series_list, series_top, maxv=100):
    
    top3, ytd, ave, future_score, point = get_ave_score(series_list)
    series_list.append(dict(name=u'2012 Top3 Ave', value=top3))
    series_list.append(dict(name=u'2012 YTD', value=ytd))
    series_list.append(dict(name=u'2011 Ave', value=ave))
    
    # Create a XYChart object of size 540 x 375 pixels
    c = XYChart(900, 320)
    # Add a title to the chart using 18 pts Times Bold Italic font
    #c.addTitle("Average Weekly Network Load", "timesbi.ttf", 18)
    title = c.addTitle(utils.to_utf8(title), "simsun.ttc", 12)
    title.setMargin2(20, 0, 10, 30)
    
    color_list = BASE_COLOR
    COLOR_BLUE = 0x0070C0
    COLOR_93 = 0x00B050
    COLOR_87 = 0xFFD600
    COLOR_TOP3_AVE = 0x595443
    COLOR_YTD = 0xFF0000
    COLOR_AVE = 0x5678A9
    
    # Set the plotarea at (50, 55) and of 440 x 280 pixels in size. Use a vertical
    # gradient color from light red (ffdddd) to dark red (880000) as background. Set
    # border and grid lines to white (ffffff).
    chart_width = 30 + 190 * len(labels) 
    c.setPlotArea(50, 90, chart_width, 200, c.linearGradientColor(60, 40, 60, 280, 0xffffff,
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
    
    c.yAxis().setLinearScale(0, maxv)
    
    # Add a multi-bar layer with 3 data sets and 4 pixels 3D depth
    #~ layer = c.addBarLayer2(Side, 1)
    
    layer = c.addBarLayer()
    layer.setBarGap(0.1)
    layer.setBarWidth(170, 18)

    for index, series in enumerate(series_list):
        values = series['value']
        if len(values) > 1:
            color = COLOR_BLUE
        else:
            values.append(future_score)
            if point == 93:
                color = COLOR_93
            elif point == 87:
                color = COLOR_87
            else:
                color = COLOR_BLUE
        name = utils.to_utf8(series['name'])
        if name == u'2012 Top3 Ave':
            color = COLOR_TOP3_AVE
        if name == u'2012 YTD':
            color = COLOR_YTD
        if name == u'2011 Ave':
            color = COLOR_AVE
        #print values, color, name
        write_list = []
        for value in values:
            if value == -1 or value > 100:
                write_list.append(0)
            else:
                write_list.append(value)
        layer.addDataSet(write_list, color, name)
        for i, v in enumerate(values):
            if v == -1 or v > 100:
                if name in (u'2012 Top3 Ave',u'2012 YTD', u'2011 Ave'):
                    layer.addCustomGroupLabel(index, i, " ")
                else:
                    layer.addCustomGroupLabel(index, i, "N/A")
            else:
                layer.setAggregateLabelFormat("{value|1}")
                layer.setAggregateLabelStyle ('', 10, '0x0000', 0)
    
    yMark = c.yAxis().addMark(point, '0x800080', '%s' % point)
    yMark.setLineWidth(1)
    yMark.setAlignment(TopCenter)

    # Set bar border to transparent. Use soft lighting effect with light direction from
    # top.
    layer.setBorderColor(Transparent, softLighting(Top))
    #layer.setBorderColor(Transparent, barLighting(0.75, 2.0))
    
    #layer.setAggregateLabelFormat("{value|1}")
    
    # output the chart
    return c.makeChart2(PNG)

def get_ave_score(series_list):
    point_93 = 93
    point_87 = 87
    year_2011 = []
    year_2012 = []
    top3 = [-1, ]
    ytd = [-1, ]
    ave = [-1, ]
    future_score = 0.0
    point = []
    for series in series_list:
        if 'W' in series['name']:
            values = series['value']
            if len(values) > 1:
                year_2011.append(values[0])
                year_2012.append(values[1])
            else:
                year_2011.append(values[0])
                
    if year_2011:
        total = 0.0
        count = len(year_2011)
        for score in year_2011:
            if score == -1:
                count -= 1
                continue
            total += score
        if count != 0:
            ave.append(total / count)
        else:
            ave.append(-1)
        
    if year_2012:
        total = 0.0
        top3_total = 0.0
        length = len(year_2012)
        count = len(year_2012)
        for score in year_2012:
            if score == -1:
                count -= 1
                continue
            total += score
        if length == 4:
            top3_list = list(year_2012).sort()
            top3_total = total - top3_list[0]
            top3.append(top3_total / 3)
        else:
            top3_total = total
            if count <= 0:
                top3.append(-1)
            else:
                top3.append(top3_total / count)
        if count <= 0:
            ytd.append(-1)
        else:
            ytd.append(total / count)
        if length == 1:
            if ytd[1] >= 72:
                future_score = (93 * 4 - ytd[1]) / 3.0
                point = point_93
            else:
                future_score = (87 * 4 - ytd[1]) / 3.0
                point = point_87
        elif length == 2:
            if ytd[1] >= 86:
                future_score = (93 * 4 - ytd[1] * 2) / 2.0
                point = point_93
            else:
                future_score = (87 * 4 - ytd[1] * 2) / 2.0
                point = point_87
        elif length == 3:
            if ytd[1] >= 90.67:
                future_score = (93 * 4 - ytd[1] * 3) / 1.0
                point = point_93
            else:
                future_score = (87 * 4 - ytd[1] * 3) / 1.0
                point = point_87
        else:
            pass
    
    return top3, ytd, ave, future_score, point

def test():
    from random import randint
    title = '经销商总得分 Total Score'
    labels = ['第一期/W1', '第二期/W2', '第三期/W3', '第四期/W4']
    data_list = []
    series_list = []
    series_list.append(dict(name=u'当前经销商得分', value=[4.1, 4.1, 4.1, 4.1, ]))
    series_list.append(dict(name=u'所属区域平均得分　', value=[14.1, 14.1, 14.1, 14.1, ]))
    series_list.append(dict(name=u'全国平均得分', value=[13.1, 13.1, 13.1, 13.1, ]))
    
    series_list.append(dict(name=u'小区平均得分', value=[12.1, 12.1, 12.1, 12.1, ]))
    series_list.append(dict(name=u'城市平均得分', value=[43.1, 43.1, 43.1, 43.1, ]))
    series_list.append(dict(name=u'省份平均得分', value=[15.1, 15.1, 15.1, 15.1, ]))
    series_list.append(dict(name=u'经销商集团平均得分', value=[24.1, 24.1, 24.1, 24.1, ]))
    series_top = dict(name=u'全国最佳经销商得分', value=[randint(1, 10) for i in labels])
    
    save_as = 'D:/test.png'
    data = create_multi_xychart(title, labels, series_list, series_top)
    file(save_as, 'wb').write(data)
    return data

def test1():
    title = '各期数得分对比'
    # The data for the bar chart
    data = [80, 90, 57, 86, 95]

    # The labels for the bar chart
    labels = ["第一期/W1", "第二期/W2", "2003", "2004", "2005"]
    
    save_as = 'r:/test1.png'
    data = create_simple_xychart(title, labels, data)
    file(save_as, 'wb').write(data)
    return data

def test2():
    from random import randint
    title = '经销商总得分 Total Score'
    labels = ['2011', '2012', ]
    data_list = []
    series_list = []
    series_list.append(dict(name=u'W1', value=[93.2, 94.1]))
    series_list.append(dict(name=u'W2', value=[87.8, ]))
    series_list.append(dict(name=u'W3', value=[94.8, ]))
    series_list.append(dict(name=u'W4', value=[91.4, ]))
    series_top = {}
    
    save_as = 'D:/test.png'
    data = create_history_now_future_xychart(title, labels, series_list, series_top)
    file(save_as, 'wb').write(data)
    return data

if __name__ == '__main__':
    test2()
