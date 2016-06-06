#encoding:utf-8

from mc.models import ReportDocument
def get_regional_report_document(term, areacode):
    '''提供某个区域内的所有report_document的查询接口，返回值为ReportDocument的queryset
    @param areacode:区域数值，具体详见mc.enums.CHOICES_AREA_TYPE
    '''
    return ReportDocument.objects.filter(term=term, areacode=areacode)
