"""경영학과 사이트 크롤링 모듈

이 모듈은 학부공지, 대학원공지, 취업게시판 크롤링을 포함합니다.
공지 리스트를 크롤링하는 리스트타입 크롤러와 공지 내용을 크롤링하는
메인 크롤러로 구성되어있습니다.

1. 학부공지 크롤러 (SbNoticeCrawler)
2. 취업게시판 크롤러 (SbCareerCrawler)

Examples:
    크롤러의 사용방법은 모두 같습니다. 다음은 학부공지 크롤러를
    활용한 예시입니다.

    >>> crawler = SbNoticeCrawler()
    >>> crawler.start()
    1페이지를 크롤링

    >>> SbNoticeCrawler(3).start()
    3페이지를 크롤링

    >>> crawler = SbNoticeCrawler()
    >>> crawler.reculsive = False
    >>> crawler.start()
    본문내용 포함하지 않고 크롤링

    >>> crawler.data
    크롤링 결과에 접근
"""
from yoncrawler.crawlers.base_cralwer import BaseCrawler
from yoncrawler.util import logger, request_module, parse_module
import datetime
import requests
from bs4 import BeautifulSoup


mylogger = logger.getMyLogger()
SUBJECT = "School of Business"


class SbCrawler(BaseCrawler):
    """경영학과 사이트의 리스트형 베이스 크롤러

    학사공지, 취업 게시판의 부모클래스입니다.
    직접 사용할 경우 오류가 발생합니다.

    Attributes:
        subject (string) : 크롤링 사이트의 주제, 디폴트는 School of Business 
        name (string) : 크롤러의 이름
        html (string) : 사이트의 html
        fileter_key (string) : db의 종복을 확인하는 키, 디폴트는 'href'로 주소를 사용
        request_method (func) : request를 실행하는 방법
        sub_crawler (crawler class) : sublist 즉 본문 내용을 크롤링 할 크롤러 클래스
        _datetime (datetime obj) : 크롤러 객체가 생성된 시간
    """

    def __init__(self):
        """SbCrawler의 생성자

        직접적인 Args는 없으므로 생성 후 직정 setting 해주어야 합니다.
        """
        super().__init__()
        self.subject = SUBJECT
        self.name = "School of Business Crawler"
        self.html = None
        self.filter_key = 'href'
        self._datetime = datetime.datetime.now()
        self.request_method = request_module.basic_request

    def request(self):
        """주어진 request method를 통해 사이트의 html을 request하여 저장
        """
        self.html = self.request_method(self.url)
        # mylogger.debug(self.html)

    def parse(self):
        """html 파일을 파싱하여 데이터를 가져옴
        """
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
        except Exception as e:
            mylogger.warning(e)

        board = soup.find('table', {'id': 'Board'})

        data = parse_module.table_parser(board)

        base_url = "https://ysb.yonsei.ac.kr/"
        for x in data:
            x['href'] = base_url + x['href']

        self._set_data(data)

    def set_page(self, page):
        """page가 주어졌을 때 page에 알맞은 url로 변경

        Args:
            page (int or None): 첫 페이지의 경우 대부분 None.
        """
        self.page = page
        if isinstance(self.page, int):
            self.url = self.url + "&page=" + str(self.page)

    def __str__(self):
        """출력 포맷

        Returns:
            str : 출력할 스트링
        """
        return f"<{self.name}> | Datetime : {self._datetime} | Address : {self.url}"


class SbMainCrawler(BaseCrawler):
    """경영학과 게시글 본문 크롤러

    주로 서브크롤러로 사용되어 공지 리스트에 존재하는 공지들의 본문을 크롤링

    Attributes:
        subject (string) : 크롤링 사이트의 주제, 디폴트는 School of Business 
        name (string) : 크롤러의 이름.
            디폴트는 "Sb Main Crawler"이지만 서브크롤러로 호출될 시
            "{Main Crawler Name}__Sb Main Crawler"로 변경
        html (string) : 사이트의 html
        request_method (func) : request를 실행하는 방법
    """

    def __init__(self):
        """SbMainCrawer의 생성자
        """
        super().__init__()
        self.subject = SUBJECT
        self.name = "Sb Main Crawler"
        self.html = None
        self.request_method = request_module.basic_request

    def request(self):
        """주어진 request method를 통해 사이트의 html을 request하여 저장
        """
        self.html = self.request_method(self.url)
        # mylogger.info(self.html)

    def parse(self):
        """html을 파싱하여 데이터를 setting

        Data Attributes:
            title : 문서의 제목
            date : 문서작성날짜 
            content : 문서 본문 html 파일
            href : 문서의 주소
        """
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
        except Exception as e:
            mylogger.warning(e)

        board = soup.find("div", {"class": "BoardWrapper"})
        data = {}
        data['title'] = board.find("div", {"id": "BoardViewTitle"}).text
        date = board.find("div", {"id": "BoardViewAdd"})
        if date is not None:
            data['date'] = date.text[4:14]
        data['content'] = str(soup.find("div", {"id": "BoardContent"}))
        data['href'] = self.url

        self._set_data(data)

    def __str__(self):
        """출력시 포맷"""
        return f"<{self.name}> | Address : {self.url}"


class SbNoticeCrawler(SbCrawler):
    """경영학과 학부공지 리스트 크롤러

    SbCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : https://ysb.yonsei.ac.kr/board.asp?mid=m06_01
    """

    def __init__(self, page=None):
        """CsNoticeCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "Bs Notice Crawler"
        self.url = "https://ysb.yonsei.ac.kr/board.asp?mid=m06_01"
        self.set_page(page)
        self.sub_crawler = SbMainCrawler
        # from yoncrawler.test.test_crawler import EmptyCrawler
        # self.sub_crawler = EmptyCrawler


class SbCareerCrawler(SbCrawler):
    """경영학과 취업공지 리스트 크롤러

    SbCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : https://ysb.yonsei.ac.kr/career.asp?mid=m08_03
    """

    def __init__(self, page=None):
        """SbCareerCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "Bs Career Crawler"
        self.url = "https://ysb.yonsei.ac.kr/career.asp?mid=m08_03"
        self.set_page(page)
        self.sub_crawler = SbMainCrawler
        # from yoncrawler.test.test_crawler import EmptyCrawler
        # self.sub_crawler = EmptyCrawler


if __name__ == "__main__":
    crawlers = [
        SbNoticeCrawler,
        SbCareerCrawler,
    ]

    for n in crawlers:
        n().start()
        print(n.data)
