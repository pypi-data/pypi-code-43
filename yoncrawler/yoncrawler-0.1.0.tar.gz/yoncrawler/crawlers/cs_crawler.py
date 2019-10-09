"""컴퓨터과학과 사이트 크롤링 모듈

이 모듈은 학부공지, 대학원공지, 장학금 게시판 크롤링을 포함합니다.
공지 리스트를 크롤링하는 리스트타입 크롤러와 공지 내용을 크롤링하는
메인 크롤러로 구성되어있습니다.

1. 학부공지 크롤러 (CsNoticeCrawler)
2. 대학원공지 크롤러 (CsGraduateNoticeCrawler)
3. 장학금게시판 크롤러 (CsScholarshipCrawler)

Examples:
    크롤러의 사용방법은 모두 같습니다. 다음은 학부공지 크롤러를
    활용한 예시입니다.

    >>> crawler = CsNoticeCrawler()
    >>> crawler.start()
    1페이지를 크롤링

    >>> CsNoticeCrawler(3).start()
    3페이지를 크롤링

    >>> crawler = CsNoticeCrawler()
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
SUBJECT = "Computer Science"


class CsCrawler(BaseCrawler):
    """컴퓨터과학과 사이트의 리스트형 베이스 크롤러

    학사공지, 대학원공지, 장학금 게시판의 부모클래스입니다.
    직접 사용할 경우 오류가 발생합니다.

    Attributes:
        subject (string) : 크롤링 사이트의 주제, 디폴트는 Computer Science
        name (string) : 크롤러의 이름
        html (string) : 사이트의 html
        fileter_key (string) : db의 종복을 확인하는 키, 디폴트는 'href'로 주소를 사용
        request_method (func) : request를 실행하는 방법
        sub_crawler (crawler class) : sublist 즉 본문 내용을 크롤링 할 크롤러 클래스
        _datetime (datetime obj) : 크롤러 객체가 생성된 시간
    """

    def __init__(self):
        """CsCrawler의 생성자

        직접적인 Args는 없으므로 생성 후 직정 setting 해주어야 합니다.
        """
        super().__init__()
        self.subject = SUBJECT
        self.name = "Computer Science Crawler"
        self.html = None
        self.filter_key = 'href'
        self.sub_crawler = CsMainCrawler
        self._datetime = datetime.datetime.now()
        # self.request_method = request_module.basic_request
        self.request_method = request_module.basic_request

    def request(self):
        """주어진 request method를 통해 사이트의 html을 request하여 저장
        """
        headers={
        "Proxy-Connection" : "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": "_INSIGHT_CK_8301=62d9962141dea25131283b2bc6708b8c_92350|83d7801103d921a0b19e3b2bc6708b8c_92350:1568894150000; AMCV_686A3E135A2FEC210A495C17%40AdobeOrg=-306458230%7CMCIDTS%7C18160%7CMCMID%7C90200592323401487385831856890001594097%7CMCOPTOUT-1568998437s%7CNONE%7CvVersion%7C3.2.0",
        "Host": "cs.yonsei.ac.kr",
        }
        self.html = self.request_method(self.url, headers=headers)
        # mylogger.debug(self.html)

    def parse(self):
        """html 파일을 파싱하여 데이터를 가져옴
        """
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
        except Exception as e:
            mylogger.warning(e)

        board = soup.find('table', {'class': 'board04'})

        # Change 2nd 번호 to 날짜
        def fix(table):
            name = table.find('tr').find_all('th')[2]
            name.string = "날짜"
            return table

        data = parse_module.table_parser(board, fix)

        base_url = "http://cs.yonsei.ac.kr/"
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


class CsMainCrawler(BaseCrawler):
    """컴퓨터과학과 게시글 본문 크롤러

    주로 서브크롤러로 사용되어 공지 리스트에 존재하는 공지들의 본문을 크롤링

    Attributes:
        subject (string) : 크롤링 사이트의 주제, 디폴트는 Computer Science
        name (string) : 크롤러의 이름.
            디폴트는 "Cs Main Crawler"이지만 서브크롤러로 호출될 시
            "{Main Crawler Name}__Cs Main Crawler"로 변경
        html (string) : 사이트의 html
        request_method (func) : request를 실행하는 방법
    """

    def __init__(self):
        """CsMainCrawer의 생성자
        """
        super().__init__()
        self.subject = SUBJECT
        self.name = "Cs Main Crawler"
        self.html = None
        # self.request_method = request_module.basic_request
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
            number : 문서 번호 
            content : 문서 본문 html 파일
            href : 문서의 주소
        """
        try:
            soup = BeautifulSoup(self.html, 'html.parser')
        except Exception as e:
            mylogger.warning(e)

        board = soup.find("table", {"class": "board05"})
        data = {}
        data['title'] = board.find("th", {"class": "subject"}).text
        data['number'] = board.find("td", {"class": "hit"}).\
            find("strong").text
        data['content'] = str(soup.find("div", {"class": "b_cont01"}))
        data['href'] = self.url

        self._set_data(data)
        # mylogger.debug(self.data)

    def __str__(self):
        """출력시 포맷"""
        return f"<{self.name}> |  Address : {self.url}"


class CsNoticeCrawler(CsCrawler):
    """컴퓨터과학과 학부공지 리스트 크롤러

    CsCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : http://cs.yonsei.ac.kr/sub05_1.php?nSeq=1
    """

    def __init__(self, page=None):
        """CsNoticeCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "CS Faculty Notice Crawler"
        self.url = "http://cs.yonsei.ac.kr/sub05_1.php?nSeq=1"
        self.set_page(page)


class CsGraduateNoticeCrawler(CsCrawler):
    """컴퓨터과학과 대학원공지 리스트 크롤러

    CsCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : http://cs.yonsei.ac.kr/sub05_1.php?nSeq=2
    """

    def __init__(self, page=None):
        """CsGraduateNoticeCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "CS Graduate School Notice Crawler"
        self.url = "http://cs.yonsei.ac.kr/sub05_1.php?nSeq=2"
        self.set_page(page)


class CsScholarshipCrawler(CsCrawler):
    """컴퓨터과학과 장학금공지 리스트 크롤러

    CsCrawler를 상속한 리스트 크롤러로 db, page, reculsive를 주로 바꾼다.
    사이트 : http://cs.yonsei.ac.kr/sub05_1.php?nSeq=3
    """

    def __init__(self, page=None):
        """CsScholarshipCrawler의 생성자

        Args:
            page (int, optional): 크롤링할 페이지. Defaults to None.
        """
        super().__init__()
        self.name = "CS Scholarship Notice Crawler"
        self.url = "http://cs.yonsei.ac.kr/sub05_1.php?nSeq=3"
        self.set_page(page)


if __name__ == "__main__":
    crawlers = [
        CsNoticeCrawler,
        CsGraduateNoticeCrawler,
        CsScholarshipCrawler
    ]

    for n in crawlers:
        n().start()
        print(n.data)
