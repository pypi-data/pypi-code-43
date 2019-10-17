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
    status = "1000"
    update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
