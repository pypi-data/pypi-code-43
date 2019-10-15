from bs4 import BeautifulSoup
from scrapy_redis_frame.common_utils import html_util


class ExtractUtil(object):

    def __init__(self, head_str: str, body_str: str):
        self.head = BeautifulSoup(head_str, "lxml")
        self.body = BeautifulSoup(body_str, "lxml")
        self.body_str = body_str

    def get_title(self):
        title = ""
        if self.head:
            title = self.head.title.text
        return title

    def get_meta_value(self, name_key, value_key="content"):
        meta_list = self.head.findAll('meta', attrs={'name': name_key})
        if len(meta_list) > 0:
            content = meta_list[0].get(value_key)
        if not content:
            content = ""
        return content

    def get_type_code(self):
        type_key_map = {
            '时政': ['时政','反腐倡廉','高层动态','组织人事'],
            '军事': ['军事'],
            '财经': ['财经'],
            '娱乐': ['娱乐'],
            '体育': ['体育','人民足球'],
            '科技': ['科技'],
            '房产': ['房产'],
            '资讯': ['资讯']
        }
        article_type = "资讯"
        path_list = self.body.find_all(class_='pos_re_search')
        if len(path_list) > 0:
            link_list = path_list[0].find_all('a')
            if len(link_list) > 0:
                for a_tag in link_list:
                    for key, value in type_key_map.items():
                        if a_tag.text.strip() in value:
                            article_type = key
                            break
        return article_type

    def get_article(self):
        article = ""
        article_soup = self.body.find_all(class_='text_con')
        if article_soup:
            body_html = article_soup[0].get_text()
        else:
            body_html = html_util.clean_html(self.body_str)
        if body_html:
            article = body_html.replace("\r", "").replace("\n", "").replace(" ", "").replace("\t", "")
        return article
