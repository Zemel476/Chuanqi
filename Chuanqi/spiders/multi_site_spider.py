import json
import importlib

import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy.exceptions import CloseSpider, IgnoreRequest

from Selenium.seleniumrequest import SeleniumRequest


class MultiSiteSpider(RedisSpider):
    name = 'chuanqi'
    redis_key = 'crawl_queue:urls'
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 60,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429]
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_request_from_data(self, data):
        try:
            task = json.loads(data.decode('utf-8'))
            meta = {
                'task_data': task,
                'dont_retry': False,
                'handle_httpstatus_list': [403, 404, 429, 500],
                'max_retry_times': 3,
                'proxy_strategy': 'rotate' if task.get('need_proxy', True) else 'none'
            }

            # 动态设置请求参数
            if task['method'] == 'POST':
                req = scrapy.FormRequest(
                    url=task['url'],
                    # json.loads 解析只能用 "双引号"
                    formdata= json.loads(task.get('payload')),
                    callback=self.parse_response,
                    meta=meta,
                    dont_filter=True
                )
            elif task['method'] == 'GET':
                req = scrapy.Request(
                    url=task['url'],
                    callback=self.parse_response,
                    meta=meta,
                    dont_filter=True
                )
            elif task['method'] == 'SELENIUM':
                req = SeleniumRequest(
                    url=task['url'],
                    callback=self.parse_response,
                    meta=meta,
                    dont_filter=True
                )
            else:
                raise NotImplementedError

            return req
        except Exception as e:
            self.logger.error(f"Request creation failed: {e}")
            raise IgnoreRequest(f"Invalid task data: {e}")

    def parse_response(self, response):
        task = response.meta['task_data']
        try:
            # 验证码处理
            if "captcha" in response.text.lower():
                return self.handle_captcha(response)

            # 动态加载解析器
            parser = self.load_parser(task['parser'])
            yield from parser.parse(response, task)
        except Exception as e:
            self.logger.error(f"Parse error: {str(e)}", exc_info=True)
            yield self.handle_failure(response, e)

    def load_parser(self, parser_name):
        try:
            module = importlib.import_module(f"Chuanqi.parsers.{parser_name}")
            return module
        except ImportError:
            self.logger.error(f"Parser module {parser_name} not found")
            raise CloseSpider(f"Parser {parser_name} not available")


    def handle_captcha(self, response):
        # 调用验证码服务
        task = response.meta['task_data']
        self.logger.info(f"Captcha detected on {task['site_id']}")
        # captcha_solution = self.crawler.engine.downloader.middleware.captcha_mw.solve_captcha(
        #     response,
        #     site_id=task['site_id']
        # )
        # if captcha_solution:
        #     return scrapy.FormRequest.from_response(
        #         response,
        #         formdata=captcha_solution,
        #         callback=self.parse_response,
        #         meta=response.meta
        #     )
        return self.handle_failure(response, "Captcha unsolved")

    def handle_failure(self, response, reason):
        task = response.meta['task_data']
        task_id = task['task_id']
        # 更新数据库状态
        # self.crawler.stats.inc_value('task/failed')
        # 失败重试逻辑
        if response.meta.get('retry_times', 0) < response.meta.get('max_retry_times', 3):
            self.logger.info(f"Retrying task {task_id}")
            return response.request.replace(dont_filter=True)
        else:
            self.logger.error(f"Task {task_id} failed: {reason}")
            # 标记任务失败
            # self.redis_conn.hset('failed_tasks', task_id, reason)
            return None