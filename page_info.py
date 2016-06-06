#encoding:utf-8
from userpro import enums
module_urls = ['ProjectOverview', 'QuestionnaireQA', 'QuestionnaireQAMINI', 'ProjectStatus', 'DealerReport']
#格式：
#中文标题，英文标题，链接地址，页面文件，能够访问的权限(空表示可以全部访问)，不能访问的权限，页面html所在目录（templates下的子目录名）
page_list = (
(u'项目介绍', 'Project Overview', ['mcview.page.overview', ], [enums.SHOW_DEALER_PAGE, enums.SHOW_ALL_PAGE, enums.SHOW_NO_RUN_PAGE, enums.FW_AREA_AUDIT_PERMISSION], [], 'projectoverview', 'ProjectOverview'),
#(u'问卷问与答', 'Q/A', ['mcview.page.questionqa', ], [enums.SHOW_DEALER_PAGE, enums.SHOW_ALL_PAGE, enums.SHOW_NO_RUN_PAGE, enums.FW_AREA_AUDIT_PERMISSION], [], 'questionqa', 'QuestionnaireQA'),
(u'问卷问与答', 'Question Q/A', ['mcview.page.questionqa', ], [enums.SHOW_DEALER_PAGE, enums.SHOW_ALL_PAGE, enums.SHOW_NO_RUN_PAGE, enums.FW_AREA_AUDIT_PERMISSION], [], 'questionqa', 'QuestionnaireQA'),
#(u'问卷问与答-MINI', 'Q/A MINI', ['mcview.page.questionqamini', ], [enums.SHOW_DEALER_PAGE, enums.SHOW_ALL_PAGE, enums.SHOW_NO_RUN_PAGE, enums.FW_AREA_AUDIT_PERMISSION], [], 'questionqabmw', 'QuestionnaireQAMINI'),
#(u'执行进度', 'Project Status', ['mcview.page.project_status', ], [enums.SHOW_ALL_PAGE, enums.FW_AREA_AUDIT_PERMISSION], [], 'projectstatus', 'ProjectStatus'),
(u'经销商单店报告', 'Dealer Report', ['mcview.page.dealer_report', ], [enums.SHOW_DEALER_PAGE, enums.SHOW_ALL_PAGE, enums.SHOW_NO_RUN_PAGE], [], 'dealerreport', 'DealerReport'),
#(u'区域报告', 'Regional Report', ['mcview.page.regional_report', ], [enums.SHOW_REGION_PAGE, enums.SHOW_NO_RUN_PAGE], [], 'regionalreport', 'RegionalReport'),
#(u'全国报告', 'National Report', ['mcview.page.national_report', ], [enums.SHOW_NATION_PAGE, enums.SHOW_NO_RUN_PAGE], [], 'nationalreport', 'NationalReport'),
)

project_style = 'style1'
project_title = u'宝马2015年APQ项目在线系统'


project_dealer_name = u'经销商'

#~ max_score = 1000

#排序
project_rank_display = {1:['total', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'I'],
                        2:['total', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'I'],
                        3:['total', 'A', 'B', 'C', 'D', 'E', 'F', 'H'],
                        4:['total', 'A', 'B', 'C', 'D', 'E', 'F'],
                        5:['total', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                        6:['total', 'A', 'B', 'C', 'D', 'E', 'F', 'G'],
                        7:['total', 'A', 'B', 'C', 'D', 'E', 'F', 'H'],
                        8:['total', 'A', 'B', 'C', 'D', 'E', 'F']}
#~ root_count = 3

#警报提示
#~ def warning(paper_id):
    #~ import json
    #~ from smk.mc.models import Paper
    #~ score_str = Paper.objects.get(id=paper_id).score_str
    #~ if score_str:
        #~ score_dict = json.loads(score_str)
        #~ if float(score_dict['total']) > 800:
            #~ return False
        #~ else:
            #~ return True
    #~ else:
        #~ return True
