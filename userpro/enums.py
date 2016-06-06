#encoding:utf-8

FW_INPUT_PERMISSION = u'评估员QC'
FW_BEGIN_AUDIT_PERMISSION = u'QC一审'
FW_QC_AUDIT_PERMISSION = u'QC二审'
FW_QC_AUDIT_PERMISSION2 = u'QC三审'
FW_AREA_AUDIT_PERMISSION = u'督导审核'
FW_AUDIT_PERMISSION = u'研究审核'
FW_END_AUDIT_PERMISSION = u'终审确认'
FH_INPUT_PERMISSION = u'复核录入'
FH_AUDIT_PERMISSION = u'复核审核'
FH_END_AUDIT_PERMISSION = u'复核终审确认'
BMW_AUDIT_PERMISSION = u'BMW审核'
TRAN_PERMISSION = u'问卷翻译'
MANAGER_PERMISSION = u'系统管理员'
SHOW_ALL_PAGE = u'前台-可看所有页面'
SHOW_NO_RUN_PAGE = u'前台-除“执行进度”与“经销商的登陆次数和时间”功能外的所有页面'
SHOW_DEALER_PAGE = u'前台-只能查看经销商页面'
#SHOW_REGION_PAGE = u'前台-只能查看区域页面'
#SHOW_NATION_PAGE = u'前台-只能查看全国页面'
SHOW_ALL_PAPERS = u'后台－能看到所有问卷'

MC_PERMISSIONS = (
FW_INPUT_PERMISSION,
FW_BEGIN_AUDIT_PERMISSION,
FW_QC_AUDIT_PERMISSION,
FW_QC_AUDIT_PERMISSION2,
FW_AREA_AUDIT_PERMISSION,
FW_AUDIT_PERMISSION,
FW_END_AUDIT_PERMISSION,
FH_INPUT_PERMISSION,
FH_AUDIT_PERMISSION,
FH_END_AUDIT_PERMISSION,
BMW_AUDIT_PERMISSION,
TRAN_PERMISSION,
MANAGER_PERMISSION,
SHOW_ALL_PAGE,
SHOW_NO_RUN_PAGE,
SHOW_DEALER_PAGE,
#SHOW_REGION_PAGE,
#SHOW_NATION_PAGE,
SHOW_ALL_PAPERS,
)

MAN_GROUP = u'系统管理员'
DEALER_GROUP = u'经销商'
AREA_GROUP = u'小区'
REGION_GROUP = u'区域'
NATION_GROUP = u'全国'
#BMW_GROUP = u'BMW'
#FW_INPUT_GROUP = u'GFK数据录入'
#FW_AUDIT_GROUP = u'GFK数据审核'
#FW_DUDAO_GROUP = u'督导审核'
#FW_TRAN_GROUP = u'翻译员'
#FH_INPUT_GROUP = u'独立复核录入'
#FH_AUDIT_GROUP = u'独立复核审核'

MC_GROUPS = (
(DEALER_GROUP, {}),
(AREA_GROUP, {}),
(REGION_GROUP, {}),
(NATION_GROUP, {}),
#(FW_INPUT_GROUP, {u'问卷':'add,change', u'图片文件':'all', u'录音文件':'all', u'Xsl Report':'all', }),
#(FW_AUDIT_GROUP, {u'问卷':'change,delete', u'问卷差异':'delete', u'问题差异':'delete', u'图片文件':'all', u'录音文件':'all', u'Xsl Report':'all', }),
#(FW_DUDAO_GROUP, {u'问卷':'change,delete', u'问卷差异':'change,delete', u'问题差异':'change,delete' , u'图片文件':'all', u'录音文件':'all', u'Xsl Report':'all', }),
#(FW_TRAN_GROUP, {u'问卷':'change' }),
#(FH_INPUT_GROUP, {u'问卷':'add,change', u'图片文件':'all', u'录音文件':'all', u'Xsl Report':'all', }),
#(FH_AUDIT_GROUP, {u'问卷':'change,delete', u'问卷差异':'delete', u'问题差异':'delete', u'图片文件':'all', u'录音文件':'all', u'Xsl Report':'all', }),
(MAN_GROUP, {u'问卷':'all', u'图片文件':'all', u'问卷差异':'change,delete', u'问题差异':'change,delete', u'录音文件':'all', u'Xsl Report':'all', 'user':'all', 'group':'all', u'Term':'all', })
)
