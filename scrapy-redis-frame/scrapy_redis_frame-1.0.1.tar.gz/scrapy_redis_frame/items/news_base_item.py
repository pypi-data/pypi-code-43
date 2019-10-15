import time
import scrapy


class NewsBaseItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    context = scrapy.Field()
    keywords = scrapy.Field()
    author = scrapy.Field()
    originalTag = scrapy.Field()
    publishTime = scrapy.Field()
    originalTag = scrapy.Field()
    articleTypeName = scrapy.Field()
    areaName = scrapy.Field()
    articleSiteRoute = scrapy.Field()
    dataSourceName = scrapy.Field()
    hotFlag = scrapy.Field()
    html = scrapy.Field()
    status = scrapy.Field().setdefault("1000")
    update_time = scrapy.Field().setdefault(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
