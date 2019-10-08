from spider.base import BaseSpider


class VideoSpider(BaseSpider):
    @classmethod
    def extract_date(cls, soup):
        try:
            author_div = soup.find_all("div", class_="author")
            date_info = author_div[0].find_all("span")[0].text
            date = "{}-{}-{}".format(date_info[:4], date_info[5:7], date_info[8:10])
        except (Exception,):
            date = None
        return date

    def extract_content(self):
        for tt, t_info in self.targets.items():
            t_soup = self.catch_html_soup(t_info["url"])
            date = self.extract_date(t_soup)
            if self.is_today and date != self.now_date:
                continue
            t_results = t_soup.find_all("div", class_="v_news_content")
            try:
                content = t_results[0].find_all("script")[0].get("vurl")
                t_info["content"] = self.process_url(content)
                t_info["category"] = "video"
            except (Exception,):
                try:
                    content = []
                    for img in t_results[0].find_all("img"):
                        img_url = img.get("src")
                        content.append(self.process_url(img_url))
                    t_info["content"] = content
                    t_info["category"] = "img"
                except (Exception,):
                    t_info["content"] = None
        return self.targets

    def collect_target(self, page_index=None, today=None):
        is_empty = True
        url = self.base_url + page_index if page_index else self.base_url + self.main_index
        soup = self.catch_html_soup(url)
        ul_results = soup.find_all("div", class_="picbox")
        for ul_r in ul_results:
            try:
                target_url = ul_r.find_all('a')[0].get('href')
                target_topic = ul_r.text
                self.targets[target_topic] = {"url": self.process_url(target_url), "topic": target_topic}
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
