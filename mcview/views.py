#encoding:utf-8
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from mcview.decorator import render_to
import mc
from service.core import _term, _user


@login_required
@render_to('super_report.html')
def super_report(request):
    from django.db import connection
    
    def get_dealer_id_list(dealer):
        """
            得到指定dealer能看到的所有dealer的id
        """
        id_list = []
        if dealer.parent:
            id_list.extend(mc.utils.get_parent_dealer_id_list(dealer.parent))
        id_list.extend(mc.utils.get_sub_dealer_id_list(dealer))
        return id_list
    
    def float_format(afloat):
        if afloat is None:
            return '&nbsp'
        return '%.2f' % afloat

    #~ if not userpro.has_all_page_perm(request.user):
        #~ raise Http404()
    current_term = _term.get_cur_term()
    
    dealer = _user.get_dealer_by_user(request.user)
    if not dealer:
        return HttpResponseRedirect('/')
    
    total_cp_list = mc.get_total_cp_list()
    dealer_id_list = get_dealer_id_list(dealer)
    
    show_dealer_search_box = True
    LEAF_DEALER_ID_SET = set(mc.get_leaf_dealer_id_for_bm())
    #~ if user.role.name == 'customer_1': #全国但不显示经销商
        #~ dealer_id_list = [id for id in dealer_id_list if id not in LEAF_DEALER_ID_SET]
        #~ show_dealer_search_box = False
    
    where_list = ['dealer_id in (%s)' % (','.join([str(id) for id in dealer_id_list]))]

    term_list = mc.get_terms()
    total_term_id_list = [t.id for t in term_list]
    term_id_list = [t for t in request.POST.getlist('term_list') if t]
    terms = None
    if not term_id_list:
        terms = request.REQUEST.get('terms')
        if terms:
            term_id_list = [int(id) for id in terms.split(',')]
    if term_id_list:
        if not terms:
            terms = ','.join([str(id) for id in term_id_list])
        where_list.append('(term_id in (%s) or term_id is null)' % (','.join([str(id) for id in term_id_list])))
    
    fixed_head_list = ['dealer_id', 'dealer_name', 'term_id', 'term_name', 'Total']
    head_name_list = [h for h in request.POST.getlist('head_name_list') if h]
    if not head_name_list:
        heads = request.REQUEST.get('heads')
        if heads:
            if heads == 'all':
                head_list = total_cp_list
            else:
                tmp_name_set = set(heads.split(','))
                head_list = [cp for cp in total_cp_list if cp.name in tmp_name_set]
        else:
            head_list = [cp for cp in total_cp_list if cp.has_child]
    else:
        tmp_name_set = set(head_name_list)
        head_list = [cp for cp in total_cp_list if cp.name in tmp_name_set]
    if head_list:
        heads = ','.join([cp.name for cp in head_list])
        total_head_list = fixed_head_list + [cp.name for cp in head_list]
    else:
        total_head_list = fixed_head_list
    sql = 'select %s from mc_report r,mc_reportdata rd,mc_dealer d where %s and r.dealer_id=d.id and r.id=rd.id order by d.listorder,r.term_id;' % (','.join(total_head_list), ' and '.join(where_list))
    sql = """select %s 
from mc_report r 
inner join mc_dealer d 
on %s and r.dealer_id=d.id
left join mc_reportdata rd 
on rd.id=r.id 
order by d.listorder,r.term_id;""" % (','.join(total_head_list), ' and '.join(where_list))
    
    #print sql
    import DbUtils
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        data_list = c.fetchall()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    row_list = []
    country_area_id_set = set([dealer.id for dealer in mc.get_regionals()])
    root_dealer = mc.get_root_dealer()
    country_area_id_set.add(root_dealer.id)
    
    DEALER_PARENT_DICT = mc.get_dealer_parent_dict()
    for data in data_list:
        dealer_id = data[0]
        term_id = data[2]
        
        dealer_disp = unicode(data[1] or '')

        leaf = ''
        term_str = ''
        if term_id:
            if dealer_id in LEAF_DEALER_ID_SET:
                leaf = ' leaf'
                dealer_disp = '<a href="/report/detail_report/%s/%s/" target="_blank">%s</a>' % (dealer_id, term_id, dealer_disp)
            td_dealer = '<td><input type="checkbox" name="dealer_%(dealer_id)s_%(term_id)s" id="dealer_%(dealer_id)s_%(term_id)s" class="cb_dealer"/></td><td class="dealer%(leaf)s nowrap">%(dealer_disp)s</td>' % vars()
            term_str = '_%s' % term_id
        else:
            td_dealer = '<td></td><td class="dealer" nowrap>%(dealer_disp)s<span class="fold closed">+</span></td>' % vars()
        td_term = '<td class="term" nowrap>%s</td>' % unicode(data[3] or '')        
        td_score_list = '</td><td>'.join(map(float_format, data[4:]))
        dealer_parent = DEALER_PARENT_DICT.get(dealer_id, '')
        if dealer_id in country_area_id_set:
            display_class = ''
        else:
            display_class = ' hide'
        
        row_list.append('<tr id="row_%(dealer_id)s%(term_str)s" class="sub_%(dealer_parent)s%(leaf)s%(display_class)s data">%(td_dealer)s%(td_term)s<td>%(td_score_list)s</td></tr>' % vars())
    cp_group_list = mc.get_checkpoint_group_list()
    #~ #判断是否显示雷达图按钮
    #~ if not settings.USE_FUSION_CHART:
        #~ c['show_radar'] = True
    return locals()
