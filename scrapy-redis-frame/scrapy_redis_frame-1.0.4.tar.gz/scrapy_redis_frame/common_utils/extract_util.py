from bs4 import BeautifulSoup
from scrapy_redis_frame.common_utils import html_util


class ExtractUtil(object):

    def __init__(self, head_str: str, body_str: str):
        self.head = BeautifulSoup(head_str, "lxml")
        self.body = BeautifulSoup(body_str, "lxml")
        self.body_str = body_str

    def get_title(self):
        title = ""
        try:
            title = self.head.title.text
            title = title.replace("\r", "").replace("\n", "")
        except:
            pass
        return title

    def get_meta_value(self, name_key, value_key="content", attr_key='name'):
        meta_list = self.head.findAll('meta', attrs={attr_key: name_key})
        content = None
        if len(meta_list) > 0:
            content = meta_list[0].get(value_key)
        if not content:
            content = ""
        return content

    def get_type_code(self):
        type_key_map = {
            '时政': ['时政', '反腐倡廉', '高层动态', '组织人事'],
            '军事': ['军事'],
            '财经': ['财经'],
            '娱乐': ['娱乐'],
            '体育': ['体育', '人民足球'],
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

    def get_content_by_p_count(self):
        content = ""
        try:
            main_div = get_main_div(self.body)
            content = get_content_div(main_div)
        except:
            pass
        return content

    def get_content_by_all_p(self):
        content_list = []
        try:
            div_p_list = self.body.find_all('p')
            for item in div_p_list:
                if is_content(item.get_text()):
                    content_list.append(item.get_text())
        except:
            pass
        return "".join(content_list)

    def get_chinese_word_count(self, content):
        word_count = 0
        for word in content:
            if '\u4e00' <= word <= '\u9fff':
                word_count = word_count + 1
        return word_count

def get_content_div(root_soup):
    content = ""
    target_div = None
    children = root_soup.children
    p_list = []
    div_max_p_count = 0
    for item in children:
        if item.name == 'div':
            p_count = get_p_count(item)
            if p_count > div_max_p_count:
                div_max_p_count = p_count
                target_div = item
        elif item.name == 'p':
            p_list.append(item)
    if len(p_list) > div_max_p_count:
        for target_p in p_list:
            content = content + target_p.get_text()
    else:
        return get_content_div(target_div)
    if not content:
        content = root_soup.get_text()
    return content


def get_p_count(div_soup):
    div_p_list = div_soup.find_all('p')
    p_count = 0
    for p_tag in div_p_list:
        content = p_tag.get_text()
        word_count = 0
        for word in content:
            if '\u4e00' <= word <= '\u9fff':
                word_count = word_count + 1
        if word_count > 10:
            p_count = p_count + 1
    return p_count


def get_main_div(div_soup):
    div = div_soup.find_all('div')
    max_div = None
    max_count = 0
    for div_soup in div:
        p_count = get_p_count(div_soup)
        if p_count > max_count:
            max_count = p_count
            max_div = div_soup
    return max_div


def is_content(content):
    word_count = 0
    for word in content:
        if '\u4e00' <= word <= '\u9fff':
            word_count = word_count + 1
    if word_count > 8:
        return True
    else:
        return False
