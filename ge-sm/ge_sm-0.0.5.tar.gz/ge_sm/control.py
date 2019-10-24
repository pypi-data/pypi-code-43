import datetime
import pandas as pd
import shutil
import os
from dateutil.relativedelta import relativedelta
# from common.logger import write_to_log
from ge_sm.facebook_code.data_creation.query_pages import construct_insight_data, get_fb_demo_data  # derive_dates
from ge_sm.facebook_code.data_creation.query_posts import construct_post_data
from ge_sm.facebook_code.data_creation.query_ads import construct_ad_data

from ge_sm.youtube_code.data_creation.query_reports import run_video_report, run_channel_report, run_demo_report

from ge_sm.google_analytics_code.data_creation.query_reports import construct_user_report, make_signedup_df

from ge_sm.common.create_database_tables import upload_with_pandas, delete_all_data
from ge_sm.control_details import reportlist

# put in path name for secrets et al as running from batch file
upload_dir = 'ge_sm/sm-upload'
pathname = os.path.join(os.path.abspath(''), upload_dir)

# from common.create_database_tables import update_monthly_table

# # set logger
# logging.basicConfig(filename='facebook_api_log',
#                     filemode='a',
#                     format='%(asctime)s - %(levelname)s - %(module)-20s: %(message)s',
#                     level=logging.DEBUG)
# log = logging.getLogger('facebook_api_log')

# @write_to_log
def main(s, page_start, e):

    user_stdt = '2019-06-12'
    post_start = '2019-06-01'

    # note adding in page / demo start dates as it only seems to like <=90 days (!)
    # demo_start = '2019-08-01'
    #
    # # # # Get various dataframes and add to dictionary
    ## FBADs
    reportlist['fb_ads']['df'] = construct_ad_data(post_start, e)

    # Other FB
    reportlist['fb_demos']['df'] = get_fb_demo_data(page_start, e, 'days_28')
    reportlist['fb_pages_day']['df'] = construct_insight_data(page_start, e, 'day')
    reportlist['fb_pages_week']['df'] = construct_insight_data(page_start, e, 'week')
    reportlist['fb_pages_days_28']['df'] = construct_insight_data(page_start, e, 'days_28')
    reportlist['fb_posts']['df'] = construct_post_data(post_start, e)

    ## YT
    reportlist['yt_channels']['df'] = run_channel_report(post_start, e)
    reportlist['yt_demos']['df'] = run_demo_report(post_start, e)
    reportlist['yt_video']['df'] = run_video_report(post_start, e)
    #
    # # # # Import kadence Id files
    df_kadence = pd.read_csv(pathname + 'common/Kadence_Ids.csv')
    df_kadence.columns = ['KadenceId', 'Centre']
    reportlist['ga_signed_up']['df'] = make_signedup_df(reportlist['ga_user_pages_CK']['df'],
                                                        reportlist['ga_user_pages_CKW']['df'],
                                                        reportlist['ga_user_events_CK']['df'],
                                                        df_kadence)
    # user_pages_dfs = construct_user_report(user_stdt, e, 'pages')

    # ## GA
    # reportlist['ga_user_pages_C']['df'] = user_pages_dfs['ga_user_pages_C']
    # reportlist['ga_user_pages_CK']['df'] = user_pages_dfs['ga_user_pages_CK']
    # reportlist['ga_user_pages_CW']['df'] = user_pages_dfs['ga_user_pages_CW']
    # reportlist['ga_user_pages_CKW']['df'] = user_pages_dfs['ga_user_pages_CKW']
    # user_events_dfs = construct_user_report(user_stdt, e, 'events')
    # reportlist['ga_user_events_C']['df'] = user_events_dfs['ga_user_events_C']
    # reportlist['ga_user_events_CK']['df'] = user_events_dfs['ga_user_events_CK']
    # reportlist['ga_user_events_CW']['df'] = user_events_dfs['ga_user_events_CW']
    # reportlist['ga_user_events_CKW']['df'] = user_events_dfs['ga_user_events_CKW']
    #


    #
    # # # # # # # Loop over each element in report list
    for rpt, data in reportlist.items():
        # if rpt != 'fb_ads' and rpt != 'fb_posts' and rpt[:2] == 'fb':
        # try:
            print(rpt)
            # First make table if need (normally keep commented out)
            #     create_table_from_csv(data['tablename'], data['tablestructure'])
            # Copy old .csv files into same location to keep them for future checking
            csvlen = len(data['outputcsvloc']) - 4
            if os.path.exists(pathname + data['outputcsvloc']):
                shutil.copy2(pathname + data['outputcsvloc'], pathname +data['outputcsvloc'][:csvlen] + '_Old.csv')
            # # Delete all data from given table
            delete_all_data(data['tablename'])
            # temp thing to sort out FB page issue on 3 months
            df = data['df']
            if data['FBPAGE'] == 'Yes':
                # get historic data for this FB object
                olddata_df = pd.read_csv(pathname + data['outputcsvloc'])
                # knock out current month then merge with downloaded data
                olddata_df['Date'] = pd.to_datetime(olddata_df['Date'].astype(str).str.slice(0, 10), format = '%Y-%m-%d')
                olddata_df = olddata_df[olddata_df['Date'] < page_start]
                df = pd.concat([olddata_df, df], ignore_index = True, sort = False)
            print(df.to_string())

            os.makedirs(os.path.dirname(pathname + data['outputcsvloc']), exist_ok=True)
            # Export dataframe to csv
            if not os.path.exists(pathname + data['outputcsvloc']):
                open(pathname + data['outputcsvloc'], 'a').close()

            df.to_csv(pathname + data['outputcsvloc'], index = False)
            # Upload to data platform
            upload_with_pandas(df, data['tablename'])
            # except:
            #     pass

if __name__ == '__main__':
    today = datetime.datetime.now()
    tm = datetime.datetime.strftime(today + datetime.timedelta(days=2), "%Y-%m-%d")
    td = datetime.datetime.strftime(today, "%Y-%m-%d")
    yd = datetime.datetime.strftime(today + datetime.timedelta(days=-1), "%Y-%m-%d")
    print(yd, td, tm)

    # keep eye on month for now
    if not os.environ.get('DYNAMIC_DATES'):
        main(
            os.environ.get('START_DATE', '2019-06-01'),
            os.environ.get('END_DATE', '2019-08-01'),
            tm
        )
    else:
        months = os.environ.get('REPORT_MONTHS', 2)
        main(
            today.replace(day=1).date().strftime('%Y-%m-%d'),
            (today - relativedelta(months=months)).replace(day=1).strftime('%Y-%m-%d'),
            tm
        )
