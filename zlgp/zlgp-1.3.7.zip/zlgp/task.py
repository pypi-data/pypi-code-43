from lmf.dbv2 import db_command ,db_query 
from zlgp import restart_quyu_union

from zlgp.dst import  api 

sql="vacuum full src.t_gg ;"


#重启时间区域
def t1():
    quyu_time=['jiangsu_suzhou_ggzy', 'xinjiang_hami_gcjs', 'henan_hebi_ggzy', 'qycg_zbb_nankai_edu_cn', 'qycg_www_soeasyjc_com', 'guangdong_zhaoqing_ggzy', 'qycg_www_zmzb_com',
     'qycg_b2b_10086_cn', 'beijing_beijingshi_gcjs', 'gansu_wuwei_ggzy', 'guangdong_guangdongsheng_1_zfcg', 'guangdong_guangdongsheng_gcjs', 'guangxi_guangxisheng_gcjs', 
     'guangxi_qinzhou_zfcg', 'heilongjiang_daqing_ggzy', 'henan_henansheng_gcjs', 'hubei_macheng_ggzy', 'hunan_xiangtan_ggzy', 'jiangsu_jiangsusheng_gcjs', 'liaoning_haicheng_ggzy', 
     'liaoning_liaoningsheng_gcjs', 'liaoning_liaoningsheng_ggzy', 'liaoning_liaoningsheng_zfcg', 'qycg_ec_chalieco_com', 'qycg_fwgs_sinograin_com_cn', 'qycg_syhggs_dlzb_com',
      'guangxi_guangxisheng_1_gcjs', 'jiangxi_nanchang_gcjs', 'liaoning_tieling_ggzy', 'qycg_bid_fujianbid_com']

    for quyu in quyu_time:

        restart_quyu_union(quyu)

def t2():
    quyu_xzqh=[ 'daili_zb_hbxttx_cn', 'daili_www_ztgh_com_cn', 'daili_www_zhongdaguoxin_com', 'daili_www_xhtc_com_cn', 'daili_www_sxzx2016_com', 'daili_www_qhbidding_com', 'daili_www_kmjl_cc',
     'daili_www_kanti_cn', 'daili_www_jczh100_com', 'daili_www_hljzxzb_com', 'daili_www_hebeihongtai_cn', 'daili_www_gzebid_com', 'daili_www_guofazhaobiao_com', 'daili_www_gmgitc_com',
      'daili_www_gdebidding_com', 'daili_www_gcbidding_com', 'daili_www_fzjtcn_com', 'daili_www_dongfengtc_com', 'daili_www_dcgczx_com', 'daili_www_cqiic_com', 'daili_www_cntcitc_com_cn',
       'daili_www_cniitc_com_cn', 'daili_www_cfet_com_cn', 'daili_www_bkpmzb_com', 'daili_www_bidding_citic', 'daili_www_baosteelbidding_com', 'daili_www_ah_inter_com', 
       'daili_tendering_sinosteel_com', 'daili_e_sinochemitc_com', 'qg_zfcg', 'qg_ggzy', 'qg_2_zfcg', 'qg_1_zfcg', 'qycg_zljt_dlzb_com', 'qycg_zgyy_dlzb_com', 'qycg_zghkyl_dlzb_com', 
       'qycg_zghkgy_dlzb_com', 'qycg_zgdzxx_dlzb_com', 'qycg_zgdxjt_dlzb_com', 'qycg_zcc_sdau_edu_cn', 'qycg_zc_gtcloud_cn', 'qycg_zbcg_nenu_edu_cn', 'qycg_zbb_nankai_edu_cn', 
       'qycg_zb_crlintex_com', 'qycg_ysky_dlzb_com', 'qycg_wzcgzs_95306_cn', 'qycg_www_zzzb_net', 'qycg_www_zybtp_com', 'qycg_www_zmzb_com', 'qycg_www_zjscs_net', 'qycg_www_zeec_cn', 
       'qycg_www_ykjtzb_com', 'qycg_www_wiscobidding_com_cn', 'qycg_www_sztc_com', 'qycg_www_soeasyjc_com', 'qycg_www_sinochemitc_com', 'qycg_www_ngecc_com', 'qycg_www_namkwong_com_mo',
        'qycg_www_mgzbzx_com', 'qycg_www_haierbid_com', 'qycg_www_dlztb_com', 'qycg_www_dlzb_com_c1608', 'qycg_www_dlzb_com', 'qycg_www_dlswzb_com', 'qycg_www_czztb_com', 
        'qycg_www_crpsz_com', 'qycg_www_crecgec_com', 'qycg_www_cr15gmc_com', 'qycg_www_cntic_com_cn', 'qycg_www_cntec_com_cn', 'qycg_www_cnpcbidding_com', 'qycg_www_cnbmtendering_com', 
        'qycg_www_chinabidding_com_total', 'qycg_www_chinabidding_com', 'qycg_www_china_tender_com_cn', 'qycg_www_chdtp_com', 'qycg_www_cgdcbidding_com', 'qycg_www_cfcpn_com', 'qycg_www_ceitcl_com', 
        'qycg_www_ceiea_com', 'qycg_www_cdt_eb_com', 'qycg_www_bidding_csg_cn', 'qycg_uat_ec_chng_com_cn', 'qycg_txzb_miit_gov_cn', 'qycg_thzb_crsc_cn', 'qycg_sytrq_dlzb_com', 
        'qycg_syhggs_dlzb_com', 'qycg_srm_crland_com_cn', 'qycg_sdhsg_com', 'qycg_scs_inspur_com', 'qycg_mall_cdtbuy_cn', 'qycg_jzcg_cfhi_com', 'qycg_gs_coscoshipping_com', 
        'qycg_fwgs_sinograin_com_cn', 'qycg_etp_fawiec_com', 'qycg_eps_shmetro_com', 'qycg_eps_sdic_com_cn', 'qycg_eps_hnagroup_com', 'qycg_epp_ctg_com_cn', 'qycg_ecp_sgcc_com_cn',
         'qycg_ecp_cgnpc_com_cn', 'qycg_ec1_mcc_com_cn', 'qycg_ec_chalieco_com', 'qycg_ec_ceec_net_cn', 'qycg_ec_ccccltd_cn', 'qycg_ebs_shasteel_cn', 'qycg_ebid_aecc_mall_com',
          'qycg_dzzb_ciesco_com_cn', 'qycg_dfqcgs_dlzb_com', 'qycg_csbidding_csair_com', 'qycg_cgw_xjbt_gov_cn', 'qycg_caigou_ceair_com', 'qycg_buy_cnooc_com_cn', 
          'qycg_bidding_sinopec_com', 'qycg_bidding_crmsc_com_cn', 'qycg_bidding_ceiec_com_cn', 'qycg_bid_powerchina_cn', 'qycg_bid_ansteel_cn', 'qycg_baowu_ouyeelbuy_com', 
          'qycg_b2bcoal_crp_net_cn', 'qycg_b2b_10086_cn']

    i=0
    for quyu in quyu_xzqh:
        i+=1
        print(i,quyu)
        api.restart_quyu(quyu)

#NameError: name 'extime_liaoning_liaoningsheng_zfcg' is not defined 
#qycg_bid_fujianbid_com

def t3():
    sql="select quyu from cfg where quyu~'^zlshenpi' order by quyu "


    df=db_query(sql,dbtype="postgresql",conp=["postgres","since2015","192.168.4.201","postgres","public"])

    quyu_shenpi=df['quyu'].tolist()


    i=0
    for quyu in quyu_shenpi:
      try:
        i+=1
        print(i,quyu)
        api.restart_quyu(quyu)
      except:
        print("-----------------------------------------------",quyu)
#zlshenpi_hebeisheng


def t4():
    sql="select quyu from cfg where quyu~'^zlsys' order by quyu "


    df=db_query(sql,dbtype="postgresql",conp=["postgres","since2015","192.168.4.201","postgres","public"])

    quyu_shenpi=df['quyu'].tolist()


    i=0
    for quyu in quyu_shenpi:
      try:
        i+=1
        print(i,quyu)
        restart_quyu_union(quyu)
      except:
        print("-----------------------------------------------",quyu)