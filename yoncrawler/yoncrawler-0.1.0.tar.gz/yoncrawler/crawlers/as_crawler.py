"""응용통계학과 사이트 크롤링 모듈

이 모듈은 학부공지, 대학원공지, 취업 게시판 크롤링을 포함합니다.
공지 리스트를 크롤링하는 리스트타입 크롤러와 공지 내용을 크롤링하는
메인 크롤러로 구성되어있습니다.
경제학과 사이트 크롤링과 매우 흡사합니다.
1. 학부공지 크롤러 (AsNoticeCrawler)
2. 대학원공지 크롤러 (AsGraduateNoticeCrawler)
3. 취업게시판 크롤러 (AsCareerCrawler)

Examples:
    크롤러의 사용방법은 모두 같습니다. 다음은 학부공지 크롤러를
    활용한 예시입니다.

    >>> crawler = AsNoticeCrawler()
    >>> crawler.start()
    1페이지를 크롤링

    >>> AsNoticeCrawler(3).start()
    3페이지를 크롤링

    >>> crawler = AsNoticeCrawler()
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
SUBJECT = "Applied Statistics"


class AsCrawler(BaseCrawler):
    """응용통계학과 사이트의 리스트형 베이스 크롤러

    학사공지, 대학원공지, 취업 게시판의 부모클래스입니다.
    직접 사용할 경우 오류가 발생합니다.

    Attributes:
        subject (string) : 크롤링 사이트의 주제, 디폴트는 Applied Statistics
        name (string) : 크롤러의 이름
        html (string) : 사이트의 html
        base_url (string) : sublist 사이트들이 기본적으로 사용하는 주소
        fileter_key (string) : db의 종복을 확인하는 키, 디폴트는 'href'로 주소를 사용
        request_method (func) : request를 실행하는 방법
        sub_crawler (crawler class) : sublist 즉 본문 내용을 크롤링 할 크롤러 클래스
        _datetime (datetime obj) : 크롤러 객체가 생성된 시간
    """

    def __init__(self):
        """AsCrawler의 생성자

        직접적인 Args는 없으므로 생성 후 직정 setting 해주어야 합니다.
        """
        super().__init__()
        self.subject = SUBJECT
        self.name = "Applied Statistics Crawler"
        self.html = None
        self.base_url = None
        self.filter_key = 'href'
        self.request_method = request_module.basic_request
        self.sub_crawler = AsMainCrawler
        self._datetime = datetime.datetime.now()

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

        board = soup.find('table', {'class': 'board-table'})

        # 상당에 고정되어 있는 공지 요소들을 제거
        def fix(table):
            for tag in table.find_all('tr', {'class': 'c-board-top-wrap'}):
                tag.extract()
            return table

        # 테이블 파서를 활용하여 table 내용을 파싱
        data = parse_module.table_parser(board, fix)

        for x in data:
            x['href'] = self.base_url + x['href']

        self._set_data(data)
        # mylogger.debug(data)

    def set_page(self, page):
        """page가 주어졌을 때 page에 알맞은 url로 변경

        Args:
            page (int or None): 첫 페이지의 경우 대부분 None.
        """
        self.page = page
        self.url = self.base_url
        if isinstance(self.page, int):
            self.url = self.base_url + \
                "?article.offset=" + str((self.page-1)*10)

    def __str__(self):
        """출력시 포맷
        """
        return f"<{self.name}> | Datetime : {self._datetime} | Address : {self.url}"


class AsMainCrawler(BaseCrawler):
    """응용통계학과 게시글 본문 크롤러

    주로 서브크롤러로 사용되어 공지 리스트에 존재하는 공지들의 본문을 크롤링

    Attributes:
        subject (string) : 크롤링 사이트의 주제, 디폴트는 Applied Statistics
        name (string) : 크롤러의 이름.
            디폴트는 "As Main Crawler"이지만 서브크롤러로 호출될 시
            "{Main Crawler Name}__As Main Crawler"로 변경
        html (string) : 사이트의 html
        request_method (func) : request를 실행하는 방법
    """

    def __init__(self):
        """AsMainCrawler의 생성자
        """
        super().__init__()
        self.subject = SUBJECT
        self.name = "As Main Crawler"
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
            date : 문서 생성 날자
            writer : 문서 작성 단체
            content : 문서 본문 html 파일
            attachment (optional) : 첨부파일 이름, 없을시 ''
            href : 문서의 주소
        """
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
        except Exception as e:
            mylogger.warning(e)

        board = soup.find("div", {"class": "board-write-wrap"})
        value_list = board.find_all('dd')
        data = {}
        data['title'] = parse_module.clean(value_list[0].text)
        data['date'] = parse_module.clean(value_list[1].text)
        data['writer'] = parse_module.clean(value_list[2].text)
        data['content'] = str(value_list[3])
        data['attachment'] = ''
        if len(value_list) == 5:
            data['attachment'] = str(value_list[4])
        data['href'] = self.url

        self._set_data(data)
        # mylogger.debug(data)

    def __str__(self):
        """출력시 포맷

        Returns:
            str : 출력 문구

        Examples:
            >>> crawler = AsMainCrawler()
            >>> crawler.url = "http://stat.yonsei.ac.kr/stat/board/under_notice.do?mode=view&articleNo=62861&article.offset=0&articleLimit=10"
            >>> print(crawler)
            <As Faculty Notice Crawler__As Main Crawler> | Address : http://stat.yonsei.ac.kr/stat/board/under_notice.do?mode=view&articleNo=62861&article.offset=0&articleLimit=10
        """
        return f"<{self.name}> | Address : {self.url}"


class AsNoticeCrawler(AsCrawler):
    """응용통계학과 학부공지 리스트 크롤러

    AsCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : http://stat.yonsei.ac.kr/stat/board/under_notice.do
    """

    def __init__(self, page=None):
        """AsNoticeCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "As Faculty Notice Crawler"
        self.base_url = "http://stat.yonsei.ac.kr/stat/board/under_notice.do"
        self.set_page(page)
        # from yoncrawler.test.test_crawler import EmptyCrawler
        # self.sub_crawler = EmptyCrawler


class AsGraduateNoticeCrawler(AsCrawler):
    """응용통계학과 대학원공지 리스트 크롤러

    AsCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : http://stat.yonsei.ac.kr/stat/board/grad_notice.do
    """

    def __init__(self, page=None):
        """AsGraduateNoticeCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "As Graduate School Notice Crawler"
        self.base_url = "http://stat.yonsei.ac.kr/stat/board/grad_notice.do"
        self.set_page(page)
        # from yoncrawler.test.test_crawler import EmptyCrawler
        # self.sub_crawler = EmptyCrawler


class AsCareerCrawler(AsCrawler):
    """응용통계학과 취업게시판 리스트 크롤러

    AsCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : http://stat.yonsei.ac.kr/stat/board/job.do
    """

    def __init__(self, page=None):
        """AsCareerCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "As Career Crawler"
        self.base_url = "http://stat.yonsei.ac.kr/stat/board/job.do"
        self.set_page(page)
        # from yoncrawler.test.test_crawler import EmptyCrawler
        # self.sub_crawler = EmptyCrawler


if __name__ == "__main__":
    crawlers = [
        AsNoticeCrawler,
        AsGraduateNoticeCrawler,
        AsCareerCrawler,
    ]

    for n in crawlers:
        n().start()
        print(n.data)
