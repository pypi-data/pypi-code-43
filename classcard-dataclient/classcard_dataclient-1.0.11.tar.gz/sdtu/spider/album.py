from spider.base import BaseSpider


class AlbumSpider(BaseSpider):

    def extract_content(self):
        for tt, t_info in self.targets.items():
            t_soup = self.catch_html_soup(t_info["url"])
            t_results = t_soup.find_all("div", class_="v_news_content")
            try:
                content = []
                for img in t_results[0].find_all("img"):
                    img_url = img.get("src")
                    content.append(self.process_url(img_url))
                t_info["content"] = content
            except (Exception,):
                t_info["content"] = []
        return self.targets

    def process_url(self, url):
        return self.base_url + url

    def find_next_page(self, soup):
        try:
            results = soup.find_all("a", class_="Next")
            for r in results:
                if r.text == "下页":
                    return r.get("href")
        except (Exception,):
            return None

    @classmethod
    def extract_date(cls, li_r):
        try:
            message = li_r.find_all("span", class_="span_2")[0].text
            date = message[-10:]
            return date
        except (Exception,):
            return None

    def collect_target(self, page_index=None, today=None):
        is_empty = True
        url = self.base_url + page_index if page_index else self.base_url + self.main_index
        soup = self.catch_html_soup(url)
        li_results = soup.find_all("li", class_="li_6")
        for li_r in li_results:
            try:
                date = self.extract_date(li_r)
                if today and date != today:
                    continue
                target_url = li_r.find_all('a')[0].get('href')
                target_topic = li_r.find_all("nobr")[0].text
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
