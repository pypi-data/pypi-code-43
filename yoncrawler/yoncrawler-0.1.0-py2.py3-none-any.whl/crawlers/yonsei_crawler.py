"""연세대학교 사이트 크롤링 모듈

이 모듈은 공지, 외부공지, 장학금 게시판 크롤링을 포함합니다.
공지 리스트를 크롤링하는 리스트타입 크롤러와 공지 내용을 크롤링하는
메인 크롤러로 구성되어있습니다.

1. 공지 크롤러 (NoticeCrawler)
2. 외부공지 크롤러 (ExternalCrawler)
3. 장학금게시판 크롤러 (ScholarshipCrawler)

Examples:
    크롤러의 사용방법은 모두 같습니다. 다음은 공지 크롤러를
    활용한 예시입니다.

    >>> crawler = NoticeCrawler()
    >>> crawler.start()
    1페이지를 크롤링

    >>> NoticeCrawler(3).start()
    3페이지를 크롤링

    >>> crawler = NoticeCrawler()
    >>> crawler.reculsive = False
    >>> crawler.start()
    본문내용 포함하지 않고 크롤링

    >>> crawler.data
    크롤링 결과에 접근
"""
from yoncrawler.crawlers.base_cralwer import BaseCrawler
from yoncrawler.util import logger, request_module
import datetime
import requests
from bs4 import BeautifulSoup

mylogger = logger.getMyLogger()
SUBJECT = "Yonsei"


class YonseiCrawler(BaseCrawler):
    """연세대학교 사이트의 리스트형 베이스 크롤러

    공지, 외부공지, 장학금 게시판의 부모클래스입니다.
    직접 사용할 경우 오류가 발생합니다.

    Attributes:
        subject (string) : 크롤링 사이트의 주제, 디폴트는 Yonsei 
        name (string) : 크롤러의 이름
        html (string) : 사이트의 html
        fileter_key (string) : db의 종복을 확인하는 키, 디폴트는 'href'로 주소를 사용
        request_method (func) : request를 실행하는 방법
        sub_crawler (crawler class) : sublist 즉 본문 내용을 크롤링 할 크롤러 클래스
        _datetime (datetime obj) : 크롤러 객체가 생성된 시간
    """

    def __init__(self):
        """YonseiCrawler의 생성자

        직접적인 Args는 없으므로 생성 후 직정 setting 해주어야 합니다.
        """
        super().__init__()
        self.subject = SUBJECT
        self.name = "Yonsei Crawler"
        self.filter_key = 'href'
        self.html = None
        self._datetime = datetime.datetime.now()
        self.request_method = request_module.basic_request
        self.sub_crawler = YonseiMainCrawler
        self.board_no = None
        self.mode = "list"

    def request(self):
        """주어진 request method를 통해 사이트의 html을 request하여 저장
        """
        params = {
            "mode" : self.mode, 
            "board_no" : self.board_no, 
            "pager.offset" : self.page}
        self.html = self.request_method(self.url, params=params)
        # mylogger.debug(self.html)

    def parse(self):
        """html 파일을 파싱하여 데이터를 가져옴

        TODO:
            안정성을 위한 추가요소
            # 1. x hsa no href key
            # 2. x['href'] is None
            # 3. self.data is None

        """
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
        except Exception as e:
            mylogger.warning(e)

        board = soup.find('ul', {'class': 'board_list'})
        # mylogger.debug(board)
        board_list = board.find_all('li', {'class': None})

        self._set_data(list(map(self._parse_list, board_list)))

    def set_page(self, page):
        """page가 주어졌을 때 page에 알맞은 url로 변경

        Args:
            page (int or None): 첫 페이지의 경우 대부분 None.
        """
        if not page:
            page = 1
        if isinstance(self.page, int):
            self.page = str((page-1)*10)

    def _parse_list(self, board):
        """공지 리스트 한 개를 파싱하는 모듈

        Args:
            board (<li> tag): 공지 한 개가 포함된 <li> tag object

        Data Attributes:
            title : 문서의 제목
            category : 문서의 주체
            date : 문서의 날짜
            href : 문서의 주제

        Returns:
            dict : 파싱한 데이터가 들어있는 dictionary
        """
        try:
            href = self.url + board.find('a')['href']
            title = board.find('strong').text.replace(
                '\r', '').replace('\n', '').replace('\t', '').strip()
            spans = board.find_all('span', {'class': 'tline'})
            category = spans[0].text
            date = spans[1].text
            board = {'href': href, 'title': title,
                     'category': category, 'date': date}
            return board
        except Exception as e:
            mylogger.warning(e)
            return None

    def __str__(self):
        """출력 포맷

        Returns:
            str : 출력할 스트링
        """
        return f"<{self.name}> | Datetime : {self._datetime} | Address : {self.url}"


class YonseiMainCrawler(BaseCrawler):
    """연세대학교 게시글 본문 크롤러

    주로 서브크롤러로 사용되어 공지 리스트에 존재하는 공지들의 본문을 크롤링

    Attributes:
        subject (string) : 크롤링 사이트의 주제, 디폴트는 Yonsei
        name (string) : 크롤러의 이름.
            디폴트는 "Yonsei Main Crawler"이지만 서브크롤러로 호출될 시
            "{Main Crawler Name}__Yonsei Main Crawler"로 변경
        html (string) : 사이트의 html
        request_method (func) : request를 실행하는 방법
    """

    def __init__(self):
        """YonseiMainCrawler의 생성자
        """
        super().__init__()
        self.subject = SUBJECT
        self.name = "Yonsei Main Crawler"
        self.html = None
        self.request_method = request_module.basic_request

    def request(self):
        """주어진 request method를 통해 사이트의 html을 request하여 저장
        """
        self.html = self.request_method(self.url)
        # mylogger.debug(self.html)

    def parse(self):
        """html을 파싱하여 데이터를 setting

        Data Attributes:
            title : 문서의 제목
            date : 문서 날짜 
            cont_area : 문서 본문 html 파일
            href : 문서의 주소
        """
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
        except Exception as e:
            mylogger.warning(e)

        board_view = soup.find('dl', {'class': 'board_view'})
        title = soup.find('title').text
        date = board_view.find('span', {'class': 'date'}).text
        cont_area = str(board_view.find('div', {'class': 'cont_area'}))
        data = {'title': title, 'date': date,
                'cont_area': cont_area, 'href': self.url}

        self._set_data(data)

    def __str__(self):
        """출력시 포맷"""
        return f"<{self.name}> |  Address : {self.url}"


class NoticeCrawler(YonseiCrawler):
    """연세대학교 공지 리스트 크롤러

    YonseiCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : https://www.yonsei.ac.kr/sc/support/notice.jsp
    """

    def __init__(self, page=None):
        """NoticeCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "Notice Crawler"
        self.url = "https://www.yonsei.ac.kr/sc/support/notice.jsp"
        self.board_no = 15
        self.set_page(page)


class ExternalCrawler(YonseiCrawler):
    """연세대학교 외부공지 리스트 크롤러

    YonseiCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : https://www.yonsei.ac.kr/sc/support/etc_notice.jsp
    """

    def __init__(self, page=None):
        """ExternalCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "External Crawler"
        self.url = "https://www.yonsei.ac.kr/sc/support/etc_notice.jsp"
        self.board_no = 43
        self.set_page(page)


class ScholarshipCrawler(YonseiCrawler):
    """연세대학교 장학금 리스트 크롤러

    YonseiCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : https://www.yonsei.ac.kr/sc/support/scholarship.jsp
    """

    def __init__(self, page=None):
        """ScholarshipCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "Scholarship Crawler"
        self.url = "https://www.yonsei.ac.kr/sc/support/scholarship.jsp"
        self.board_no = 29
        self.set_page(page)

    def _parse_list(self, board):
        """장학금 리스트 한 개를 파싱하는 모듈

        Args:
            board (<li> tag): 장학금공지 한 개가 포함된 <li> tag object

        Data Attributes:
            title : 문서의 제목
            category : 문서의 주체
            start_date : 장학금 시작 날짜
            end_date : 장학금 종료 날짜
            href : 문서의 주제

        Returns:
            dict : 파싱한 데이터가 들어있는 dictionary
        """
        try:
            href = self.url + board.find('a')['href']
            title = board.find('strong').text.replace(
                '\r', '').replace('\n', '').replace('\t', '').strip()
            category = board.find('span', {'class': 'title'}).find_all(text=True, recursive=False)[2]\
                .replace('\r', '').replace('\n', '').replace('\t', '').strip()
            spans = board.find_all('span', {'class': 'tline'})
            date = spans[0].text
            start_date, end_date = date.split("~")
            board = {'href': href, 'title': title, 'category': category,
                     'start_date': start_date, 'end_date': end_date}

            # mylogger.debug(board)
            return board
        except Exception as e:
            mylogger.warning(e)
            return None


if __name__ == '__main__':
    n = ScholarshipCrawler()
    n.start()
