from yoncrawler.util.logger import getMyLogger
from abc import ABC, abstractmethod
import copy

# TODO : 서브크롤러를 돌릴지 말지에 선택할 수 있는 기능 추가
# TODO : 서브크롤러 결과에 대한 리턴을 받을 수 있어야 함.
class BaseCrawler(ABC):
    """크롤러클래스를 위한 추상클래스 입니다.

    모든 크롤러클래스는 BaseCrawler를 상속해야 합니다.

    Raises:
        NotImplementedError: BaseCrawler를 상속한 자식클래스가
            @abstractmethod로 설정된 추상메소드를 오버라이딩하지
            않을 때 발생하는 오류입니다.

    Attributes:
        _url (string) : 크롤링할 url
        _db (db object) : yoncrawler.db에 존재하는 db 오브젝트
        _data (list of dict) : 크롤링 한 데이터
        _sublist (list of string) : 연쇄적으로 크롤링할 페이지 리스트
        _sub_crawler (crawler class) : _sublist를 크롤링할 크롤러클래스
        _sub_crawler_list (list of crawler obj) : 생성된 sub_crawler 객체를 저장한 리스트
        _page (int) : 크롤링 할 페이지
        filter_key (string) : db에 이미 존재하는지 확인하는 데 사용하는 키
        subject (string) : 크롤링하는 사이트를 표현
        name (string) : 크롤러의 이름
        recursive (boolean) : sub_crawler를 사용할지 여부
        logger (object) : logger를 위한 object
    """

    def __init__(self):
        """상속된 클래스가 가질 attributes
        """
        self._url = None
        self._db = None
        self._data = None
        self._sublist = None
        self._sub_crawler = None
        self._sub_crawler_list = list()
        self._page = None
        self.filter_key = None
        self.subject = None
        self.name = None
        self.recursive = True
        self.logger = getMyLogger()

    @property
    def url(self):
        """_url 속성의 getter
        """
        return self._url

    @url.setter
    def url(self, url):
        """_url 속성의 setter

        Args:
            url (string): 크롤링할 url
                자식클래스에서 사용하지만, 생성된 객체가 사용할 일은 드물다.
        """
        self._url = url

    @property
    def db(self):
        """_db 속성의 getter
        """
        return self._db

    @db.setter
    def db(self, db):
        """_db 속성의 setter

        Args:
            db (db class): 저장을 위해 사용하는 class
        """
        db_instance = db(db_name=self.subject,
                         table_name=self.name)
        self._db = db_instance

    @property
    def sub_crawler(self):
        """_sub_crawler 속성의 getter
        """
        return self._sub_crawler

    @sub_crawler.setter
    def sub_crawler(self, crw):
        """_sub_crawler 속성의 setter

        Args:
            crw (crawler class): sub crawler 생성에 사용될 class
        """
        self._sub_crawler = crw

    @property
    def sub_crawler_list(self):
        """_sub_crawler_list 속성의 getter
        """
        return self._sub_crawler_list

    @property
    def sublist(self):
        """_sublist 속성의 getter
        """
        return self._sublist

    @sublist.setter
    def sublist(self, subs):
        """_sublist 속성의 setter

        Args:
            subs (list of string): subcrawling 할 url list
        """
        self._sublist = subs

    @property
    def page(self):
        """_page 속성의 getter
        """
        return self._page

    @page.setter
    def page(self, pg):
        """_page의 setter

        Args:
            pg (int or string): 크롤링할 페이지
        """
        if not isinstance(pg, int):
            try:
                pg = int(pg)
            except Exception:
                self.logger.warning(f"Page should be int, but now it is {pg}, type: {type(pg)}")
                return
        self._page = pg

    @property
    def data(self):
        """_data 속성의 getter
        """
        return self._data

    def _set_data(self, data):
        """_data 속성의 setter

        만약 저장된 데이터와 중복되었을 시 제외하고 저장 후,
        서브리스트를 생성한다.

        Args:
            data (list of dict): 크롤링한 결과
        """
        data = self.reduce_duplicate(data)
        self._data = data
        if isinstance(data, list):
            self.sublist = [x['href'] for x in data]

    def call_sub_crawler(self):
        """suvcrawler를 생성 후 시작한다.

        sublist를 크롤링하는 함수

        Raises:
            NotImplementedError: _sub_crawler가 지정되지 않았는데,
                _sublist가 존재할 때 발생
        TODO :
            - 멀티쓰레딩 실시
        """
        # TODO : Add multi sub_crawler for next page
        if self._sub_crawler is None:
            if self._sublist is not None:
                raise NotImplementedError
        elif self.recursive:
            # TODO Change to multithread friendly with thread pool
            for sub_url in self._sublist:
                sub_crawler = self._sub_crawler()
                sub_crawler.url = sub_url
                sub_crawler.name = self.name + "__" + sub_crawler.name
                sub_crawler._db = self.db
                if sub_crawler.db is not None:
                    sub_crawler.db.table_name = sub_crawler.name
                    sub_crawler.db.connect()
                sub_crawler.start()
                self._sub_crawler_list.append(sub_crawler)

    def start(self):
        """크롤링을 실행하는 함수

        실제 유저가 사용할 함수

        Examples:
            >>> SomeCrawler.start()
        """
        self.logger.info(f"{self}\n Crawl Start")
        self.request()
        self.parse()
        self.save()
        self.call_sub_crawler()
        self.logger.info(f"{self}\n Crawl End")

    @abstractmethod
    def request(self):
        """서버에 request를 요청하여 html을 받는다

        Raises:
            NotImplementedError: 오버라이딩 하지 않을시 발생
        """
        raise NotImplementedError

    @abstractmethod
    def parse(self):
        """html로 부터 데이터를 파싱

        Raises:
            NotImplementedError: 오버라이딩 하지 않을 시 발생
        """
        raise NotImplementedError

    def save(self):
        """데이터를 db에 저장한다.

        db object가 있다면, db 인스턴스에게 데이터를 넘긴다.

        Returns:
            [type]: [description]
        """
        if self.db is None:
            self.logger.info(
                f"{self.subject} | {self.name} | {self.url} | {self.db} | Insert Suceess")
            return self.data
        self.db.create(self.data)
        self.logger.info(
            f"{self.subject} | {self.name} | {self.url} | {self.db} | Insert Suceess")

    def reduce_duplicate(self, data):
        """이미 db에 존재하는 중복 데이터를 제거한다

        Args:
            data (list of dict): url로부터 크롤링한 데이터

        Returns:
            list of dict : 중복데이터가 사라진 데터
        """
        if self.db is not None and self.filter_key is not None:
            data = list(filter(lambda x: self.db.read(
                self.filter_key, x[self.filter_key]) is None, data))
            if len(data) == 0:
                data = None
        return data
