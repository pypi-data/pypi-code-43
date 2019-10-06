import pandas as pd 
import requests
from bs4 import BeautifulSoup
import time 
import random

def keywords_f(soup_obj):
    """
    Get keywords from html(soup) and returns a list of keywords
    """
    for script in soup_obj(["script", "style"]):
        script.extract() # Remove these two elements from the BS4 object
    text = soup_obj.get_text() 
    lines = (line.strip() for line in text.splitlines()) # break into line
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each
    text = ''.join(chunk for chunk in chunks if chunk).encode('utf-8') # Get rid of all blank lines and ends of line
    try:
        text = text.decode('unicode_escape').encode('ascii', 'ignore') # Need this as some websites aren't formatted
    except:                                                          
        return
    text = text.decode('utf-8')                                                       
    text = re.sub("[^a-zA-Z+3]"," ", text)  
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text) # Fix spacing issue from merged words
    text = text.lower().split()  # Go to lower case and split them apart
    text = [w for w in text if not w in stop_words]
    text = list(set(text)) #only care about if a word appears, don't care about the frequency
    keywords = [str(word) for word in text if word in overall_dict] #if a skill keyword is found, return it.
    return keywords

def getJobMetaData(start_url, max_results):
    """
    Gets data from Indeed.ca based on a starting url
        start_url = place to start searching for jobs, assumed to be a valid url
        max_results = maximum number of jobs to search for (should be the same as num_pages*10)
    """
    columns = ["job_title", "company_name", "location", "summary"]
    metadata_df = pd.DataFrame(columns = columns)
    ## Make sure the internet is active
    print(start_url)
    page = requests.get(start_url)
    for start in range(0, max_results, 10):
      ### Probably getting an error because I'm opening too many tabs, gotta restart every 5 just like the other searcher
      try:
          if max_results <= 10:
              page = requests.get(start_url,timeout=5)
          else: 
              page = requests.get(start_url + '&start=' + str(start),timeout=5)
          #page = requests.get('https://ca.indeed.com/jobs?q=developer+co-op&l='+ str(city) + '&start=' + str(start),timeout=5)
          page.raise_for_status()
      except requests.exceptions.RequestException as err:
          print ("OOps: Something Else",err)
          pass
      except requests.exceptions.HTTPError as errh:
          print ("Http Error:",errh)
          pass
      except requests.exceptions.ConnectionError as errc:
          print ("Error Connecting:",errc)
          pass
      except requests.exceptions.Timeout as errt:
          print ("Timeout Error:",errt)
          pass
      # if the page does not get a new page, simply move on
      if page.status_code == 404:
          continue
      #j = random.randint(1000,2200)/1000.0
      j = random.randint(1000,2000)/1000.0
      time.sleep(j) #waits for a random time so that the website don't consider you as a bot
      soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
      for div in soup.find_all(name="div", attrs={"class":"row"}): 
        #specifying row num for index of job posting in dataframe
        num = (len(metadata_df) + 1) 
        #creating an empty list to hold the data for each posting
        job_post = [] 
        #append city name
        #grabbing job title
        for a in div.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
          job_post.append(a["title"]) 
        #grabbing company name
        company = div.find_all(name="span", attrs={"class":"company"}) 
        if len(company) > 0: 
          for b in company:
            job_post.append(b.text.strip()) 
        else: 
          sec_try = div.find_all(name="span", attrs={"class":"result-link-source"})
          for span in sec_try:
            job_post.append(span.text) 
        #grabbing location name
        c = div.findAll('span', attrs={'class': 'location'}) 
        for span in c: 
          job_post.append(span.text) 
        #grabbing summary text
        d = div.findAll('span', attrs={'class': 'summary'}) 
        for span in d:
            job_post.append(span.text.strip()) 
    #appending list of job post info to dataframe at index num
        metadata_df.loc[num] = job_post
    return metadata_df



  def get_statscan():
  """Gets statscan data of interest
  For details see the statistics canada documentation and api reference.
  """
  response = requests.get(' https://www150.statcan.gc.ca/n1/dai-quo/ssi/homepage/ind-econ.json')
  data = response.json()
  # Name to label to column, find internal statscan data source or worst case just use a reference based approach
  registry_num = [3496, 3555, 3537, 3628, 3592, 3587, 3587, 3569, 3556, 3389, 5421, 3313, 3605, 3612, 3660, 4822, 19277]
  results = data['results']
  indicators = results['indicators']
  val_list = filter(lambda x: x['registry_number'] in registry_num, indicators)
  ind_list = list(val_list)
  # remove geocodes, refer to sample data from json file
  int_list = [0, 10]
  new_list = filter(lambda x: x['geo_code'] in int_list, ind_list)
  global_df = pd.DataFrame()
  for i in new_list:
    code = i['geo_code']
    val = i['value']['en']
    title = i['title']['en']#
    refper = i['refper']['en']
    growth = ''
    details = ''
    if i['growth_rate']:
      if i['growth_rate']['growth']:
        growth = i['growth_rate']['growth']['en']
        details = i['growth_rate']['details']['en']
    local_df = pd.DataFrame([[code,val,title,refper,growth,details]])
    global_df = global_df.append(local_df,ignore_index =True)
  return global_df


def exchange_rates():
  """
  """
  cfg = get_config()
  exchanges_prices_url = '{}/{}'.format('https://api.exchangeratesapi.io', 'latest?base=USD')
  response = requests.get(exchanges_prices_url)
  data = response.json()
  keep_keys = ['CAD', 'USD', 'EUR']
  rates = data['rates']
  # Clean up later
  rates_dict = {k: rates[k] for k in keep_keys}
  ex_rates_df = pd.Series(rates_dict).to_frame()
  return ex_rates_df


def csvs_to_df(path):
    """
        Input:
            path: Full path to list of csvs
        Output:
            returns: dataframe containing all the entires merged together
    """
    # get all the csv files
    allFiles = glob.glob(path + "/*.csv")

    list_ = []

    for file_ in allFiles:
        df = pd.read_csv(file_,index_col=None, header=0)
        list_.append(df)

    frame = pd.concat(list_, axis = 0, ignore_index = True)
    return frame


def drop_df_cols(dataframe):
    df = dataframe
    df = df.drop_duplicates(subset='ID', keep="last")
    if 'Applications' in df.columns:
        cols = [0,1,3]
    else:
        cols = [0,1,3,10]
    # add in check in applications column is present.
    print(df)
    df.drop(df.columns[cols],axis=1,inplace=True)
    print(df)
    df.set_index('ID',inplace=True)
    frame = df
    return frame

def create_combined_csv(path,savefile):
    frame = csvs_to_df(path)
    frame = drop_df_cols(frame)
    frame.to_csv(savefile)
    return frame