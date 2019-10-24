import pandas as pd

from facebook_business import FacebookSession, FacebookAdsApi
from facebook_business.adobjects.campaign import Campaign as AdCampaign
from facebook_business.adobjects.adaccount import AdAccount

# This is api key file location
# going forward move perhaps to api_code folder?
from ge_sm.facebook_code.api_code.facebook_secrets import long_access_token as access_token, secret as app_secret, app_id
from ge_sm.facebook_code.settings.chaa_jaa_ad_account_settings import chaa_jaa_ad_account
from ge_sm.facebook_code.settings.chaa_jaa_ad_account_settings import campaign_output_details as co
from ge_sm.facebook_code.settings.chaa_jaa_ad_account_settings import result_dict

def get_campaigns(ad_account, api_session):
    """gets campaign ids for specific ad account"""
    FacebookAdsApi.set_default_api(api_session)
    acc = AdAccount(ad_account)
    campaign_objs = [campaign for campaign in acc.get_campaigns(fields=[AdCampaign.Field.name])]
    all_campaigns = [c for c in campaign_objs]
    return campaign_objs, all_campaigns

def construct_adset_df(ad_dict_list, met_order, met_split):
    adset_data = []
    #loop over all ad in list of dictionaries
    for ad in ad_dict_list:
        adfields = ad['ad_fields']; admetrics = ad['ad_metrics']
        # default set all fields to be None
        ad_data = {}
        for m in met_order:
            ad_data[m] = None
        ad_data['campaignId'] = ad['campaignId']
        ad_data['campaignName'] = ad['campaignName']
        ad_data['status'] = ad['status']
        #now set all relevant values in ad field
        for ad_key, ad_val in adfields.items():
            #print(ad_key, ad_val)
            ad_data[ad_key] = ad_val
        # if there is any sort of metric data
        if admetrics != None:
            for in_key, in_val in admetrics.items():
                # If split metric then go inside of list
                if in_key in met_split:
                    # Look for various wanted metrics (note this is a list of dictionaries bizarrely)
                    for m in in_val:
                        # make name as in dictionary field (note key of dict is action_type)
                        metname = in_key + '_' + m['action_type']
                        # If one of the desired fields, set dataframe dictionary value
                        if metname in met_order:
                            # Only add if this field > 0
                            if float(m['value']) > 0 : ad_data[metname] = float(m['value'])
                # just for cost per thru play .. very odd
                elif in_key == 'cost_per_thruplay':
                     # weirdly it's a list with a value, no idea what's going on here
                    ad_data['cost_per_thruplay'] = in_val[0]['value']
                 # Else just set value if key there
                else:
                    ad_data[in_key] = in_val
            #sort out liftime budget
            if ad_data['lifetime_budget'] == None: ad_data['lifetime_budget'] = 0
            ad_data['lifetime_budget'] = float(ad_data['lifetime_budget']) / 100
            # sort out the nonsense about the result thing
            # and add in the cpr if can work out what it is
            ad_data['cpr'] = 0
            # get actual optimisation goal
            temp = ad_data['optimization_goal']
            # if it is one of the known goals
            if temp in result_dict:
                #if there is a cost per dict value somewhere
                if ad_data[result_dict[temp][1]] != None:
                    # set cpr to be this cost per result
                    ad_data['cpr'] = float(ad_data[result_dict[temp][1]])
                    # if this is non-zero try to back-calculate the result; needed as seem to be
                    # missing the actual value half the time!
                    if ad_data['cpr'] > 0:
                        ad_data['results'] = int(float(ad_data['spend']) / ad_data['cpr'])
                ad_data['optimization_goal'] = result_dict[temp][0]
            # add all ad data as new element of a list
            adset_data.append(ad_data)
    return pd.DataFrame(adset_data)

def construct_ad_data(stdate, eddate):

    # here we get fields / metrics we need
    ad_field_list = []; ad_met_list = []
    ad_metrics_order = []; ad_split = {}; ad_metrics_names = []
    for p, q in co.items():
        # append GE names for dataframe
        ad_metrics_names.append(p)
        #if a field / metric / split metric add to post_metrics
        if q[2] != None:
            # If property of adset, not insight then add to adset field list
            if q[2] == 'Adset':
                ad_field_list.append(q[0])
                ad_metrics_order.append(q[0])
            # If insight then add to adset insight list
            elif q[2] == 'Metric':
                ad_met_list.append(q[0])
                ad_metrics_order.append(q[0])
            else:
                # Here we deal with the metric splits in usual way (see post stuff)
                ad_metrics_order.append(q[0] + '_' + q[2])
                ad_met_list.append(q[0])
                if q[0] in ad_split:
                    ad_split[q[0]].append(q[2])
                else:
                    ad_split[q[0]] = [q[2]]
        else:
            #If one of the non field / metrics then just add to order list of df
            ad_metrics_order.append(q[0])

    # Some sort of crummy FB session stuff
    session = FacebookSession(app_id, app_secret, access_token)
    api = FacebookAdsApi(session)
    FacebookAdsApi.set_default_api(api)

    # Here we get all the ads for this account
    acc = AdAccount(chaa_jaa_ad_account['accountId'])
    # get all campaign objects
    campaign_objs = [campaign for campaign in acc.get_campaigns(fields=['name', 'status', 'start_time','stop_time'])]
    compaigns = {}
    # get some properties of each campaign
    for c in campaign_objs:
        compaigns[c['id']] = (c['name'], c['status'], c['start_time'],c['stop_time'])

    # get all adsets for this ad account
    alladsets = [adset for adset in acc.get_ad_sets(fields = ad_field_list)]

    adset_details = []  ## get ad details first
    # parameters for the adsets
    insight_params = {'time_range': {'since': stdate, 'until': eddate}}
    for ad in alladsets:
        # get all insights for this particular addset id accoun
        camp = compaigns[ad['campaign_id']]
        # print(camp)
        # get campaign details
        ad_dict = {'campaignId': ad['campaign_id'], 'campaignName': camp[0],'status': camp[1],
                   'ad_fields': ad, 'ad_metrics': None}
        # ge ad insights
        ad_insights = ad.get_insights(fields = ad_met_list, params = insight_params)
        # Now get the relevant insights
        if len(ad_insights) > 0: ad_dict['ad_metrics'] = ad_insights[0]
        # print(ad_dict)
        adset_details.append(ad_dict)
    df_ad_insights = construct_adset_df(adset_details, ad_metrics_order, ad_split)
    # now do some tidying of data
    df_ad_insights = df_ad_insights[ad_metrics_order]
    df_ad_insights.columns = ad_metrics_names

    #sort out the date fields
    df_ad_insights['Starts'] = pd.to_datetime(df_ad_insights['Starts'].str.slice(0, 10),
                                               format='%Y-%m-%d',  errors='coerce')
    df_ad_insights['Ends'] = pd.to_datetime(df_ad_insights['Ends'].str.slice(0, 10),
                                               format='%Y-%m-%d',  errors='coerce')
    #
    # Now do something about the very odd delivery thing:
    # if active and > today - day (today is 12 at night time)
    print(df_ad_insights.to_string())
    df_ad_insights.loc[(df_ad_insights['Delivery status'] == 'ACTIVE') &
           (df_ad_insights['Ends'] >= (pd.to_datetime('today') - pd.Timedelta('7 days'))), 'temp'] = 'Recently Completed'
    # if active and ends within 7 days
    df_ad_insights.loc[(df_ad_insights['Delivery status'] == 'ACTIVE') &
           (df_ad_insights['Ends'] >= pd.to_datetime('today') - pd.Timedelta('1 day')), 'temp'] = 'Active'
    # if active and ends after 7 days
    df_ad_insights.loc[(df_ad_insights['Delivery status'] == 'ACTIVE') &
           (df_ad_insights['Ends'] < (pd.to_datetime('today') - pd.Timedelta('7 days'))), 'temp'] = 'Completed'
    # else inactive
    df_ad_insights.loc[df_ad_insights['Delivery status'] != 'ACTIVE', 'temp'] = 'Inactive'
    df_ad_insights['Delivery status'] = df_ad_insights['temp']
    df_ad_insights = df_ad_insights.drop('temp', axis=1)
    return df_ad_insights

if __name__ == '__main__':

    main()