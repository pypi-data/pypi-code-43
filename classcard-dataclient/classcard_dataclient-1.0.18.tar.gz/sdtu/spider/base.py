import requests
import json
import os
import datetime
import traceback
from bs4 import BeautifulSoup
from utils.dateutils import date2str
from config import JSON_PATH


class BaseSpider(object):
    max_num = 20
    page_url = [("http://www.sdnu.edu.cn/sdyw/", "cksdywgd.htm"),
                ("http://www.sdnu.edu.cn/zhxw/", "ckzhxwgd.htm"),
                ("http://www.sdnu.edu.cn/mtsd/", "ckmtsdgd.htm"),
                ("http://www.qlshx.sdnu.edu.cn/", "tzgg.htm"),
                ("http://www.qlshx.sdnu.edu.cn/", "jzyg.htm")]

    def __init__(self, base_url, main_index):
        is_today_env = "{}_IS_TODAY".format(self.__class__.__name__.upper())
        self.is_today = os.environ.get(is_today_env, True)
        self.targets = {}
        self.base_url = base_url
        self.main_index = main_index
        now = datetime.datetime.now()
        self.now_date = date2str(now.date())

    def process_url(self, url):
        if "http" not in url:
            base_url = self.base_url if self.base_url[-1] == "/" else self.base_url + '/'
            return base_url + url if url[0] != '/' else base_url + url[1:]
        return url

    @staticmethod
    def catch_html_soup(url):
        response = requests.get(url)
        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def find_next_page(self, soup):
        try:
            results = soup.find_all("a", class_="Next")
            for r in results:
                if r.text == "下页":
                    return r.get("href")
        except (Exception,):
            return None

    @classmethod
    def extract_date(cls, soup):
        try:
            year = soup.find_all("span", class_="date")[0].text
            date = soup.find_all("span", class_="year")[0].text
            date = date.replace("/", "-")
            return "{}-{}".format(year, date)
        except (Exception,):
            return None

    def extract_content(self):
        for tt, t_info in self.targets.items():
            t_soup = self.catch_html_soup(t_info["url"])
            t_results = t_soup.find_all("div", class_="v_news_content")
            try:
                p_content = [str(p_tag) for p_tag in t_results[0].find_all("p")]
                t_info["content"] = "".join(p_content)
            except (Exception,):
                t_info["content"] = None
        return self.targets

    def collect_target(self, page_index=None, today=None):
        is_empty = True
        url = self.base_url + page_index if page_index else self.base_url + self.main_index
        soup = self.catch_html_soup(url)
        li_results = soup.find_all("li")
        for li_r in li_results:
            try:
                r = li_r.find_all('h4')[0]
                date = self.extract_date(li_r)
                if today and date != today:
                    continue
                target_url = r.find_all('a')[0].get('href')
                target_topic = r.text
                self.targets[target_topic] = {"url": self.process_url(target_url), "date": date, "topic": target_topic}
                if len(self.targets) >= self.max_num:
                    return
                is_empty = False
            except (Exception,):
                pass
        if not is_empty:
            next_page = self.find_next_page(soup)
            if next_page:
                self.collect_target(page_index=next_page, today=today)
        return

    def dump_json(self):
        string = json.dumps(dict)
        file_name = "{}_{}.json".format(self.__class__.__name__, self.now_date)
        file_path = os.path.join(JSON_PATH, file_name)
        if not os.path.exists(JSON_PATH):
            os.mkdir(JSON_PATH)
        if os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, 'w')as f:
            f.write(string)

    def start(self):
        try:
            if self.is_today:
                self.collect_target(today=self.now_date)
            else:
                self.collect_target()
            self.extract_content()
        except (Exception,):
            print(traceback.print_exc())
