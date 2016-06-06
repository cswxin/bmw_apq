#encoding:utf-8
import os, sys

sys.path.insert(0, os.path.abspath(os.curdir))
from service.easyExcel import easyExcel
from releaseinfo import REL_SITE_ROOT
from survey.models import QuestionQANew, QuestionQAColor
DOC_ROOT = os.path.join(REL_SITE_ROOT, 'doc')

def insert_questionqa(brand, sheet_index):
    file_name = u'2015 APQ Questionnaire_20150108-final.xlsx'
    xls_file = os.path.join(DOC_ROOT, file_name)
    wb = easyExcel(xls_file)

    ascii_digital = 64
    part_name = ''
    part_name_en = ''
    part_letter = ''
    part_parent = ''
    q_parent = ''
    q_number = ''
    q_color = QuestionQAColor.objects.get(name=u'流程质量部分')
    green_list = ['3',
                  '7a', '7b', '7c',
                  '12a', '12b', '12c', '12d', '12e', '12f', '12g', '12h', '12i',
                  '13a', '13b', '13c', '13d',
                  '21',
                  '34a', '34b', '34c',
                  '44a', '44b', '44c',
                  '47', '49', '53', '55', '56', '60', '61', '62', '63', '59']
    for col in range(4, 299):

        en_sheet_index = sheet_index - 1
        row_a = wb.getRangeVal(sheet_index, 'A%s' % col)
        row_b = wb.getRangeVal(sheet_index, 'B%s' % col)
        row_c = wb.getRangeVal(sheet_index, 'C%s' % col)
        row_d = wb.getRangeVal(sheet_index, 'D%s' % col)
        row_e = wb.getRangeVal(sheet_index, 'E%s' % col)
        row_a_en = wb.getRangeVal(en_sheet_index, 'A%s' % col)
        row_b_en = wb.getRangeVal(en_sheet_index, 'B%s' % col)
        row_c_en = wb.getRangeVal(en_sheet_index, 'C%s' % col)
        row_e_en = wb.getRangeVal(en_sheet_index, 'E%s' % col)
        if row_b:
            row_b.strip()
        if row_c:
            row_c.strip()
        if row_d != None:
            try:
                row_d = str(int(row_d)).strip()
            except:
                row_d = str(row_d).strip()
        if row_e:
            row_e.strip()
            row_e = row_e.replace(u'\n', u'<br />')
        if row_b_en:
            row_b_en.strip()
        if row_c_en:
            row_c_en.strip()
        if row_e_en:
            row_e_en.strip()
            row_e_en = row_e_en.replace(u'\n', u'<br />')
        if row_a != None:
            if row_b == None:
                part_name = row_a
                if hasattr(part_name, 'strip'):
                    part_name = part_name.strip()
                part_name_en = row_a_en
                if hasattr(part_name_en, 'strip'):
                    part_name_en = part_name_en.strip()
                ascii_digital += 1
                part_letter = chr(ascii_digital)
                print brand, part_letter, part_name
                part_parent, create = QuestionQANew.objects.get_or_create(brand=brand,
                                                               part=part_letter,
                                                               name_cn=part_name,
                                                               name_en=part_name_en,
                                                               has_child=True)

            if row_b != None:
                try:
                    q_number = str(int(row_a)).strip()
                except:
                    q_number = str(row_a).strip()
                print '\t', part_letter, q_number
                print '\t\t', row_c, row_d
                if q_number in green_list:
                    q_color = QuestionQAColor.objects.get(name=u'客户对待部分')
                else:
                    q_color = QuestionQAColor.objects.get(name=u'流程质量部分')
                q_parent, create = QuestionQANew.objects.get_or_create(
                                                               number=q_number,
                                                               question_cn=row_b,
                                                               question_en=row_b_en,
                                                               desc_cn=row_e,
                                                               desc_en=row_e_en,
                                                               color=q_color,
                                                               parent=part_parent,
                                                               has_child=True)
                q_parent.save()
                QuestionQANew.objects.get_or_create(
                                                    option_cn=row_c,
                                                    option_en=row_c_en,
                                                    point=row_d,
                                                    parent=q_parent)
        else:
            if row_b == None:
                print '\t\t', row_c, row_d
                QuestionQANew.objects.get_or_create(
                                                    option_cn=row_c,
                                                    option_en=row_c_en,
                                                    point=row_d,
                                                    parent=q_parent)

    wb.save()
    wb.close()

def init_questionqacolor():
    q_color1, create = QuestionQAColor.objects.get_or_create(name=u'流程质量部分')
    q_color1.color = 'white'
    q_color1.save()
    q_color2, create = QuestionQAColor.objects.get_or_create(name=u'客户对待部分')
    q_color2.color = 'lightgreen'
    q_color2.save()

def init_questionqa():
    brand = 'BMW_2015'
    sheet_index = 2
    insert_questionqa(brand, sheet_index)

    brand = 'MINI_2015'
    sheet_index = 4
    insert_questionqa(brand, sheet_index)

if __name__ == "__main__":
    init_questionqacolor()
    init_questionqa()
