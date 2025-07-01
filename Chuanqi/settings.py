BOT_NAME = "Chuanqi"

SPIDER_MODULES = ["Chuanqi.spiders"]
NEWSPIDER_MODULE = "Chuanqi.spiders"

REDIS_CLUSTER = [
    {"host": "127.0.0.1", "port": 6379},
]

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"

ADDONS = {}
LOG_LEVEL = "ERROR"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 3

# 下载器中间件
DOWNLOADER_MIDDLEWARES = {
   # "Chuanqi.middlewares.middlewares.ChuanqiDownloaderMiddleware": 500,

   # 自定义中间件
   "Chuanqi.middlewares.headers.SmartHeaderMiddleware": 600,
   # "Chuanqi.middlewares.proxy.SmartProxyMiddleware": 601,
   "Chuanqi.middlewares.selenium.SeleniumMiddleware": 602,
}


# 对Scrapy-Redis 进行配置 固定配置
# 配置调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 配置过滤器去重逻辑
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 如果为真 关闭时自动保存请求信息，如果为否则不保存。  断点续爬
SCHEDULER_PERSIST = True

ITEM_PIPELINES = {
   "Chuanqi.pipelines.ChuanqiPipeline": 300, # 正常管道
    # "scrapy_redis.pipelines.RedisPipeline": 400, # 配置redis的pipline 会自动将结果保存到redis
}

FEED_EXPORT_ENCODING = "utf-8"
