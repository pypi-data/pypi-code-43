from yoncrawler.crawlers import cs_crawler, sb_crawler, yonsei_crawler, ec_crawler, as_crawler
from yoncrawler.db import simple_db

def _getCrawlerWithNoneDB(crawler, page=None):
    n = crawler(page=page)
    n.start()
    return n.data

def _getCrawlerWithTinyDB(crawler, page=None):
    n = crawler(page=page)
    n.db = simple_db.TinyDBSaver
    n.start()
    return n.data

def getYonseiNotice(page=None):
    return _getCrawlerWithNoneDB(yonsei_crawler.NoticeCrawler, page)

def getYonseiExternal(page=None):
    return _getCrawlerWithNoneDB(yonsei_crawler.ExternalCrawler, page)

def getYonseiScholarship(page=None):
    return _getCrawlerWithNoneDB(yonsei_crawler.ScholarshipCrawler, page)

def getCsNotice(page=None):
    return _getCrawlerWithNoneDB(cs_crawler.CsNoticeCrawler, page)

def getCsGraduateNotice(page=None):
    return _getCrawlerWithNoneDB(cs_crawler.CsGraduateNoticeCrawler, page)

def getCsScholarship(page=None):
    return _getCrawlerWithNoneDB(cs_crawler.CsScholarshipCrawler, page)

def getSbNotice(page=None):
    return _getCrawlerWithNoneDB(sb_crawler.SbNoticeCrawler, page)

def getSbCareer(page=None):
    return _getCrawlerWithNoneDB(sb_crawler.SbCareerCrawler, page)

def getEcNotice(page=None):
    return _getCrawlerWithNoneDB(ec_crawler.EcNoticeCrawler, page)

def getEcGraduateNotice(page=None):
    return _getCrawlerWithNoneDB(ec_crawler.EcGraduateNoticeCrawler, page)

def getEcSeminar(page=None):
    return _getCrawlerWithNoneDB(ec_crawler.EcSeminarCrawler, page)

def getEcCareer(page=None):
    return _getCrawlerWithNoneDB(ec_crawler.EcCareerCrawler, page)

def getAsNotice(page=None):
    return _getCrawlerWithNoneDB(as_crawler.AsNoticeCrawler, page)

def getAsGraduateNotice(page=None):
    return _getCrawlerWithNoneDB(as_crawler.AsGraduateNoticeCrawler, page)

def getAsCareer(page=None):
    return _getCrawlerWithNoneDB(as_crawler.AsCareerCrawler, page)

def getYonseiNoticeJson(page=None):
    return _getCrawlerWithTinyDB(yonsei_crawler.NoticeCrawler, page)

def getYonseiExternalJson(page=None):
    return _getCrawlerWithTinyDB(yonsei_crawler.ExternalCrawler, page)

def getYonseiScholarshipJson(page=None):
    return _getCrawlerWithTinyDB(yonsei_crawler.ScholarshipCrawler, page)

def getCsNoticeJson(page=None):
    return _getCrawlerWithTinyDB(cs_crawler.CsNoticeCrawler, page)

def getCsGraduateNoticeJson(page=None):
    return _getCrawlerWithTinyDB(cs_crawler.CsGraduateNoticeCrawler, page)

def getCsScholarshipJson(page=None):
    return _getCrawlerWithTinyDB(cs_crawler.CsScholarshipCrawler, page)

def getSbNoticeJson(page=None):
    return _getCrawlerWithTinyDB(sb_crawler.SbNoticeCrawler, page)

def getSbCareerJson(page=None):
    return _getCrawlerWithTinyDB(sb_crawler.SbCareerCrawler, page)

def getEcNoticeJson(page=None):
    return _getCrawlerWithTinyDB(ec_crawler.EcNoticeCrawler, page)

def getEcGraduateNoticeJson(page=None):
    return _getCrawlerWithTinyDB(ec_crawler.EcGraduateNoticeCrawler, page)

def getEcSeminarJson(page=None):
    return _getCrawlerWithTinyDB(ec_crawler.EcSeminarCrawler, page)

def getEcCareerJson(page=None):
    return _getCrawlerWithTinyDB(ec_crawler.EcCareerCrawler, page)

def getAsNoticeJson(page=None):
    return _getCrawlerWithTinyDB(as_crawler.AsNoticeCrawler, page)

def getAsGraduateNoticeJson(page=None):
    return _getCrawlerWithTinyDB(as_crawler.AsGraduateNoticeCrawler, page)

def getAsCareerJson(page=None):
    return _getCrawlerWithTinyDB(as_crawler.AsCareerCrawler, page)