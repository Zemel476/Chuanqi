import scrapy


class ChuanqiItem(scrapy.Item):
    id = scrapy.Field() # id
    carrier = scrapy.Field() # 船东
    ship_name = scrapy.Field() # 船名
    voyage_no = scrapy.Field() # 航次

